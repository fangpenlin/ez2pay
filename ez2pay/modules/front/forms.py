from __future__ import unicode_literals

from wtforms import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import validators

from ez2pay.i18n import LocalizerFactory

get_localizer = LocalizerFactory()


class FormFactory(object):
    
    def __init__(self, localizer):
        self.localizer = localizer
        _ = self.localizer
        self.required_msg = _(u'This field is required.')
        self.invalid_email_msg = _(u'Invalid email address.')
    
    def make_contact_form(self):
        _ = self.localizer

        class ContactForm(Form):
            email = TextField(_(u'Email address'), [
                validators.Required(self.required_msg),
                validators.Email(self.invalid_email_msg)
            ])
            content = TextAreaField(_(u'Content'), [
                validators.Required(self.required_msg)
            ])
        return ContactForm
