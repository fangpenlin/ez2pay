from __future__ import unicode_literals

import balanced
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound

from ez2pay.i18n import normalize_locale_name
from ez2pay.i18n import LocalizerFactory
from ez2pay.utils import check_csrf_token
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


@view_config(route_name='front.payment', 
             renderer='templates/payment.genshi')
def payment(request):
    # TODO: get the form record from database and determine which account
    # for processing the payment, and what kind of limitation we have here
    _ = get_localizer(request)
    factory = FormFactory(_)
    PaymentForm = factory.make_payment_form()
    form = PaymentForm()

    if request.method == 'POST':
        check_csrf_token(request)

        # TODO: tokenlize the card
        payment_uri = request.params['payment_uri']
        print '#'*10, payment_uri

        balanced.configure('ef13dce2093b11e388de026ba7d31e6f')
        customer = balanced.Customer()
        customer.save()
        customer.add_card(payment_uri)
        customer.debit(
            amount=12345,
            source_uri=payment_uri,
            description='Payment made via EZ2Pay for XXX',
        )
        return dict(form=form, processed=True)
        # TODO: call the balanced API, charge the card

    return dict(form=form, processed=False)
