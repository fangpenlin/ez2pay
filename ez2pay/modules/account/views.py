from __future__ import unicode_literals

import transaction
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden

from ez2pay.models.user import UserModel
from ez2pay.mail import render_mail
from ez2pay.mail import send_mail
from ez2pay.i18n import LocalizerFactory
from ez2pay.utils import check_csrf_token
from .forms import FormFactory

get_localizer = LocalizerFactory()


@view_config(route_name='account.login', 
             renderer='templates/login.genshi')
@view_config(context='pyramid.httpexceptions.HTTPForbidden',
             renderer='templates/login.genshi')
def login(request):
    """Display login form or do login
    
    mainly borrowed from 
    https://docs.pylonsproject.org/projects/pyramid/1.1/tutorials/wiki/authorization.html?highlight=login#adding-login-and-logout-views
    
    """
    from ez2pay.models.user import BadPassword
    from ez2pay.models.user import UserNotExist
    
    _ = get_localizer(request)
    
    referrer = request.url
    my_url = request.route_url('account.login')
    if referrer == my_url:
        referrer = request.route_url('front.home')
        # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    
    username_or_email = ''
    password = ''
    
    factory = FormFactory(_)
    LoginForm = factory.make_login_form()
    form = LoginForm(request.params)
    
    if request.method == 'POST' and form.validate():
        username_or_email = request.params['username_or_email']
        password = request.params['password']
        error = False
        session = request.db_session
        user_model = UserModel(session)
        try:
            user_id = user_model.authenticate_user(username_or_email, password)
        except (UserNotExist, BadPassword):
            msg = _(u'Wrong username or password')
            request.add_flash(msg, 'error')
            return dict(
                came_from=came_from,
                username_or_email=username_or_email,
                password=password,
                form=form,
            )
            
        if user_id is not None and not error:
            headers = remember(request, user_id)
            
            user = user_model.get(user_id)
            msg = _(u"Welcome back, ${user_name}", 
                    mapping=dict(user_name=user.user_name))
            request.add_flash(msg)
            return HTTPFound(location=came_from,
                             headers=headers)

    return dict(
        came_from=came_from,
        username_or_email=username_or_email,
        password=password,
        form=form,
    )


@view_config(route_name='account.logout')
def logout(request):
    _ = get_localizer(request)
    
    referrer = request.referrer
    my_url = request.route_url('account.logout')
    # never use the login form itself as came_from
    # or, there is no referer
    if referrer == my_url or not referrer:
        referrer = request.route_url('front.home') 
    came_from = request.params.get('came_from', referrer)
    
    session = request.db_session
    user_model = UserModel(session)
    user_id = authenticated_userid(request)
    if user_id is None:
        raise HTTPBadRequest('You are not logged in')
    
    user = user_model.get(user_id)
    if user is None:
        raise HTTPBadRequest
    
    headers = forget(request)
    name = user.display_name or user.user_name
    msg = _(u"Hope we will see you soon, ${user_name}",
            mapping=dict(user_name=name))
    
    request.add_flash(msg)
    return HTTPFound(location=came_from,
                     headers=headers)


@view_config(route_name='account.register', 
             renderer='templates/register.genshi')
def register(request):
    _ = get_localizer(request)
    settings = request.registry.settings
    
    user_model = UserModel(request.db_session)
    
    factory = FormFactory(_)
    RegisterForm = factory.make_register_form()
    form = RegisterForm(request.params)
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        user_name = request.params['user_name']
        password = request.params['password']
        email = request.params['email']

        black_domain = set(settings.get('email_black_domain_list', []))
        domain = email.split('@')[-1].lower()
        if domain in black_domain:
            msg = _(u'Invalid email address')
            form.email.errors.append(msg)
            validate_result = False
        
        by_name = user_model.get_by_name(user_name)
        if by_name is not None:
            msg = _(u'Username %s already exists') % user_name
            form.user_name.errors.append(msg)
            validate_result = False
            
        by_email = user_model.get_by_email(email)
        if by_email is not None:
            msg = _(u'Email %s already exists') % email
            form.email.errors.append(msg)
            validate_result = False

        if validate_result:
            with transaction.manager:
                
                user_id = user_model.create(
                    user_name=user_name,
                    display_name=user_name,
                    password=password,
                    email=email,
                )
                
                auth_secret_key = settings['auth_secret_key']
                code = user_model.get_verification_code(
                    user_id=user_id, 
                    verify_type='create_user',
                    secret=auth_secret_key
                )
                link = request.route_url(
                    'account.activate', 
                    user_name=user_name, 
                    code=code
                )
                params = dict(link=link, user_name=user_name)
                html = render_mail(
                    request, 
                    'ez2pay:templates/mails/register_link.genshi', 
                    params
                )
                
                subject = _('ez2pay account activation')
                send_mail(
                    request=request,
                    subject=subject,
                    to_addresses=[email],
                    format='html',
                    body=html
                )
            
            msg = _(u"User ${user_name} has been registered", 
                    mapping=dict(user_name=user_name))
            request.add_flash(msg, 'success')
            return HTTPFound(location=request.route_url('account.check_mailbox'))
    
    return dict(form=form)


@view_config(route_name='account.check_mailbox', 
             renderer='templates/check_mailbox.genshi')
def check_mailbox(request):
    return dict()


@view_config(route_name='account.activate', 
             renderer='templates/activate.genshi')
def activate(request):
    _ = get_localizer(request)
    settings = request.registry.settings
    
    user_model = UserModel(request.db_session)
    
    code = request.matchdict['code']
    user_name = request.matchdict['user_name']
    user = user_model.get_by_name(user_name)
    
    auth_secret_key = settings['auth_secret_key']
    valid_code = user_model.get_verification_code(
        user_id=user.user_id, 
        verify_type='create_user',
        secret=auth_secret_key
    )
    
    if valid_code != code:
        msg = _(u"Invalid activation link", 
                mapping=dict(user_name=user_name))
        return HTTPForbidden(msg)
    
    if not user.verified:
        with transaction.manager:
            user_model.update_user(user.user_id, verified=True)
    
    msg = _(u"User ${user_name} is activated", 
            mapping=dict(user_name=user_name))
    request.add_flash(msg, 'success')
    return dict()


@view_config(route_name='account.forgot_password',
             renderer='templates/forgot_password.genshi')
def forgot_password(request):
    """Display forgot password form or do the password recovery
    
    """
    import urllib
    
    settings = request.registry.settings
    _ = get_localizer(request)
    
    factory = FormFactory(_)
    ForgotPasswordForm = factory.make_forgot_password_form()
    form = ForgotPasswordForm(request.params)
    session = request.db_session
    user_model = UserModel(session)

    if request.method == 'POST' and form.validate():
        email = request.params['email']
        
        user = user_model.get_by_email(email)
        if user is None:
            msg = _(u'Cannot find the user')
            form.email.errors.append(msg)
            return dict(form=form)
        
        user_name = user.user_name
        user_id = user.user_id
            
        # TODO: limit frequency here

        # generate verification
        auth_secret_key = settings['auth_secret_key']
        code = user_model.get_recovery_code(auth_secret_key, user_id)
        
        link = request.route_url('account.recovery_password')
        query = dict(user_name=user_name, code=code)
        link = link + '?' + urllib.urlencode(query)

        params = dict(link=link, user_name=user_name)
        html = render_mail(
            request,
            'ez2pay:templates/mails/password_recovery.genshi',
            params
        )
        
        send_mail(
            request=request,
            subject=_('ez2pay password recovery'),
            to_addresses=[email],
            format='html',
            body=html
        )
        request.add_flash(_(u'To reset your password, please check your '
                            'mailbox and click the password recovery link'))
        
    return dict(form=form)


@view_config(route_name='account.recovery_password',
             renderer='templates/recovery_password.genshi')
def recovery_password(request):
    """Display password recovery form or do the password change
    
    """
    _ = get_localizer(request)
    settings = request.registry.settings
    
    user_model = UserModel(request.db_session)
    
    user_name = request.params['user_name']
    code = request.params['code']

    user = user_model.get_by_name(user_name)
    if user is None:
        return HTTPNotFound(_('No such user %s') % user_name)
    user_id = user.user_id

    # generate verification
    auth_secret_key = settings['auth_secret_key']
    valid_code = user_model.get_recovery_code(auth_secret_key, user_id)

    if code != valid_code:
        return HTTPForbidden(_('Bad password recovery link'))
    
    factory = FormFactory(_)
    RecoveryPasswordForm = factory.make_recovery_password_form()
    form = RecoveryPasswordForm(request.params, user_name=user_name, code=code)
    
    invalid_msg = _(u'Invalid password recovery link')
    redirect_url = request.route_url('front.home')

    user = user_model.get_by_name(user_name)
    if user is None:
        request.add_flash(invalid_msg, 'error')
        raise HTTPFound(location=redirect_url)
    user_id = user.user_id
    
    if request.method == 'POST' and form.validate():
        new_password = request.POST['new_password']

        with transaction.manager:
            user_model.update_password(user_id, new_password)

        msg = _(u'Your password has been updated')
        request.add_flash(msg, 'success')
        raise HTTPFound(location=redirect_url)

    return dict(form=form)
