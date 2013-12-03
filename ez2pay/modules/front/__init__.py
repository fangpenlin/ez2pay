from __future__ import unicode_literals


def includeme(config):
    config.add_route('front.home', '/')
    config.add_route('front.set_lang', '/set_lang/{lang}')
    config.add_route('front.terms_of_service', '/terms_of_service')
    config.add_route('front.payment', '/payment')
