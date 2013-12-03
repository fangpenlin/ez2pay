from __future__ import unicode_literals

from wtforms import Form
from wtforms import TextField
from wtforms import HiddenField

from ez2pay.i18n import LocalizerFactory

get_localizer = LocalizerFactory()


class FormFactory(object):
    
    def __init__(self, localizer):
        self.localizer = localizer
        _ = self.localizer
        self.required_msg = _(u'This field is required.')
    
    def make_payment_form(self):
        _ = self.localizer

        class PaymentForm(Form):
            first_name = TextField(_('First name'), [
            ])
            last_name = TextField(_('Last name'), [
            ])
            card_number = TextField(_('Card number'), [
            ])
            expire_year = TextField(_('Expire Year (e.g. 2013)'), [
            ])
            expire_month = TextField(_('Expire month (e.g. 10)'), [
            ])
            security_code = TextField(_('Security code'), [
            ])
            payment_uri = HiddenField(_(''), [
            ])
        return PaymentForm 
