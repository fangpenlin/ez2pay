from __future__ import unicode_literals

from pyramid.request import Request
from pyramid.decorator import reify
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.settings import asbool

from ez2pay.i18n import normalize_locale_name


@subscriber(NewRequest)
def select_lanuage(event):
    """Select language from accept-languages header of request
    
    """
    request = event.request
    if request.cookies.get('_LOCALE_'):
        return
    settings = request.registry.settings
    offers = [lang.replace('_', '-').lower() 
              for lang, _ in settings['available_langs']]
    accept = request.accept_language
    match = accept.best_match(offers, settings['default_locale_name'])
    match = match.replace('-', '_')
    match = normalize_locale_name(match)
    request._LOCALE_ = match
    request.response.set_cookie('_LOCALE_', match)


@subscriber(NewRequest)
def expose_dummy_mailer(event):
    """Expose dummy mailer in WSGI mailer, mainly for testing
        
    """
    from pyramid_mailer import get_mailer
    request = event.request
    settings = request.registry.settings
    use_dummy_mailer = asbool(settings.get('use_dummy_mailer', False))
    if use_dummy_mailer:
        request.environ['pyramid_mailer.dummy_mailer'] = get_mailer(request)


class WebRequest(Request):
    
    @reify
    def db_session(self):
        """Session object for database operations
        
        """
        settings = self.registry.settings
        return settings['session']
    
    @reify
    def user_id(self):
        """Current logged in user object
        
        """
        from pyramid.security import authenticated_userid
        user_id = authenticated_userid(self)
        return user_id
    
    @reify
    def user(self):
        """Current logged in user
        
        """
        from .models.user import UserModel
        if self.user_id is None:
            return None
        model = UserModel(self.db_session)
        user = model.get(self.user_id)
        return user

    @reify
    def route_name(self):
        """Return route name if available, otherwise None is returned

        """
        return self.matched_route.name if self.matched_route else None

    @reify
    def real_ip(self):
        """The real IP address from x-forwarded-for, or x-real-ip, mainly
        depends on configuration
        
        """
        addresses = self.headers.get('X-Forwarded-For')
        if not addresses:
            return self.remote_addr
        parts = addresses.split(',')
        return parts[0].strip()
    
    def add_flash(self, *args, **kwargs):
        from .flash import add_flash
        return add_flash(self, *args, **kwargs)
