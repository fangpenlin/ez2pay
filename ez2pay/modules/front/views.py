from __future__ import unicode_literals

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound

from ez2pay.i18n import normalize_locale_name
from ez2pay.i18n import LocalizerFactory
from ez2pay.mail import send_mail
from .forms import FormFactory

get_localizer = LocalizerFactory()


@view_config(route_name='front.home', 
             renderer='templates/home.genshi')
def home(request):
    return dict()


@view_config(route_name='front.set_lang')
def set_lang(request):
    """Set current language
    
    """
    lang = request.matchdict['lang'].lower()
    langs = dict(request.registry.settings['available_langs'])
    if lang not in langs:
        raise HTTPBadRequest('Not supported language %r' % lang)
    
    referrer = request.referer
    my_url = request.route_url('front.set_lang', lang=lang)
    if referrer == my_url or not referrer:
        # never use the set_lang itself as came_from
        # which could lead to a infinite loop
        referrer = '/'  
    came_from = request.params.get('came_from', referrer)
    response = HTTPFound(location=came_from)
    response.set_cookie('_LOCALE_', normalize_locale_name(lang))
    return response


@view_config(route_name='front.terms_of_service', 
             renderer='templates/terms_of_service.genshi')
def terms_of_service(request):
    return dict()


@view_config(route_name='front.contact_us_received', 
             renderer='templates/contact_us_received.genshi')
def contact_us_received(request):
    return dict()


@view_config(route_name='front.contact_us', 
             renderer='templates/contact_us.genshi')
def contact_us(request):
    _ = get_localizer(request)
    
    factory = FormFactory(_)
    ContactForm = factory.make_contact_form()
    form = ContactForm(request.params)

    if request.method == 'POST' and form.validate():
        email = request.params['email']
        content = request.params['content']
      
        cfg = request.registry.settings['contact_us']
        recipients = cfg['recipients']
        cc = cfg['cc']
        
        headers = ['%s: %s' % (key, value) 
                   for key, value in request.headers.iteritems()]
        headers = '\n'.join(headers)
        params = dict(
            short_content=content[:10],
            content=content,
            email=email,
            remote_addr=request.real_ip,
            headers=headers,
        )
        
        mail_template = """
Mail from ez2pay contacts page
------------------------------
Sender mail: %(email)s
Content: 

%(content)s

------------------------------
Remote-Address: %(remote_addr)s

Headers: 
%(headers)s

"""
        body = mail_template % params

        subject = cfg['subject'] % params
        subject = subject.replace('\n', ' ')
        subject = subject.replace('\r', ' ')
        send_mail(
            request=request,
            subject=subject,
            to_addresses=recipients,
            cc_addresses=cc,
            reply_addresses=email,
            format='text',
            body=body
        )
        
        msg = _(u'We have received your message, thank you')
        request.add_flash(msg, 'success')
        return HTTPFound(location=request.route_url('front.contact_us_received'))
        
    return dict(form=form)
