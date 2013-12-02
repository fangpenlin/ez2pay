from __future__ import unicode_literals

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.settings import asbool
from pyramid_beaker import session_factory_from_settings

from .auth import get_group
from .models import setup_database
from .request import WebRequest
from .utils import load_app_cfg


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    
    """
    # load app cfg
    app_cfg = load_app_cfg()
    settings.update(app_cfg)
    
    # setup database
    settings = setup_database(global_config, **settings)
    authentication_policy = AuthTktAuthenticationPolicy(
        secret=settings['auth_secret_key'],
        callback=get_group)
    authorization_policy = ACLAuthorizationPolicy()
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          session_factory=session_factory,
                          request_factory=WebRequest)
    # activate translation
    config.add_translation_dirs('ez2pay:locale/')
    # add the mailer
    config.include('pyramid_mailer')
    if asbool(settings.get('use_dummy_mailer', False)):
        config.include('pyramid_mailer.testing')
    # add Genshi renderer
    config.include('pyramid_genshi')
    # setup modules
    config.include('.modules')
    # add static view
    config.add_static_view('static', 'ez2pay:static')
    # scan modules
    config.scan()
    return config.make_wsgi_app()
