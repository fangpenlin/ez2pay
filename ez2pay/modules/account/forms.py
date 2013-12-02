from __future__ import unicode_literals

from wtforms import Form
from wtforms import TextField
from wtforms import PasswordField
from wtforms import HiddenField
from wtforms import BooleanField
from wtforms import ValidationError
from wtforms import validators

from ez2pay.i18n import LocalizerFactory

get_localizer = LocalizerFactory()


def are_similar(left, right):
    """Return are two strings too similar
    
    """
    left = left.lower()
    right = right.lower()
    if left == right:
        return True
    if left and left in right:
        return True
    if right and right in left:
        return True
    return False


def similar(target, message):
    """This validator make sure that two fileds are not too similar. Mainly
    for comparing password and user name
    
    """
    def callee(form, field):
        try:
            other = form[target]
        except KeyError:
            raise ValidationError(
                field.gettext(u"Invalid field name '%s'.") % target)
        
        other_data = other.data.lower()
        my_data = field.data.lower()
        if are_similar(other_data, my_data):
            raise ValidationError(message)
    return callee


class FormFactory(object):
    
    def __init__(self, localizer):
        self.localizer = localizer
        _ = self.localizer
        self.required_msg = _(u'This field is required.')
        self.invalid_email_msg = _(u'Invalid email address.')
        self.password_not_match_msg = _(u'Password must match')
        
    def make_login_form(self):
        _ = self.localizer
        
        class LoginForm(Form):
            username_or_email = TextField(_(u'Username or Email'), [
                validators.Required(self.required_msg),
            ])
            password = PasswordField(_(u'Password'), [
                validators.Required(self.required_msg),
            ])
        return LoginForm

    def make_forgot_password_form(self):
        _ = self.localizer

        class ForgotPasswordForm(Form):
            email = TextField(_(u'Email'), [
                validators.Required(self.required_msg),
                validators.Email(self.invalid_email_msg)
            ])
        return ForgotPasswordForm
    
    def make_recovery_password_form(self):
        _ = self.localizer

        class RecoveryPasswordForm(Form):
            new_password = PasswordField(_(u'Password'), [
                validators.Required(self.required_msg),
                validators.Length(min=6)
            ])
            new_password_confirm = PasswordField(_(u'Confirm Password'), [
                validators.Required(self.required_msg),
                validators.EqualTo('new_password', 
                                   message=self.password_not_match_msg)
            ])
            user_name = HiddenField()
            code = HiddenField()
        return RecoveryPasswordForm

    def make_register_form(self):
        _ = self.localizer
        
        invalid_user_name_msg = _(u'Can only contain alphabets, numbers and '
                                  'underscores, for example "john_1987"')
        password_too_similar_msg = _(u'Password is too similar to user name.')
        terms_msg = _(u'You must accept the Terms of Service to complete '
                      'registration')
        email_not_match_msg = _(u'Email must match')
        
        class RegisterForm(Form):
            user_name = TextField(_(u'Username'), [
                validators.Required(self.required_msg),
                validators.Regexp('^([a-zA-Z0-9_])+$', 
                                  message=invalid_user_name_msg),
                validators.Length(min=2, max=16)
            ])
            email = TextField(_(u'Email'), [
                validators.Required(self.required_msg),
                validators.Email(self.invalid_email_msg),
                validators.EqualTo('email_confirm', 
                                   message=email_not_match_msg)
            ])
            email_confirm = TextField(_(u'Confirm Email'), [
                validators.Required(self.required_msg),
                validators.Email(self.invalid_email_msg)
            ])
            password = PasswordField(_(u'Password'), [
                validators.Required(self.required_msg),
                similar('user_name', password_too_similar_msg),
                validators.Length(min=6)
            ])
            terms_of_service = BooleanField('', [
                validators.Required(terms_msg)
            ])
        return RegisterForm
