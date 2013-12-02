from __future__ import unicode_literals

from wtforms import Form
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectMultipleField
from wtforms import ValidationError
from wtforms import validators
from wtforms.widgets.core import html_params
from wtforms.widgets.core import HTMLString

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


class CheckboxList(object):
    """
    Renders a checkbox list field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = [u'<ul %s>' % html_params(**kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(field.name, val, label, selected))
        html.append(u'</ul>')
        return HTMLString(u''.join(html))

    @classmethod
    def render_option(cls, name, value, label, selected, **kwargs):
        from cgi import escape
        options = dict(
            kwargs, 
            value=value,
            type='checkbox',
            id='%s-%s' % (name, value),
            name=name
        )
        if selected:
            options['checked'] = True
        return HTMLString(
            """\
            <li>
                <div class="checkbox">'
                    <label>
                        <input {params}></input>
                        {label}
                    </label>
                </div>
            </li>
            """
            .format(
                params=html_params(**options),
                label=escape(unicode(label)),
            )
        )


class FormFactory(object):
    
    def __init__(self, localizer):
        self.localizer = localizer
        _ = self.localizer
        self.required_msg = _(u'This field is required.')
        self.invalid_email_msg = _(u'Invalid email address.')
        self.password_not_match_msg = _(u'Password must match')
        self.password_too_similar_msg = \
            _(u'Password is too similar to user name.')
    
    def make_user_create_form(self):
        _ = self.localizer
        
        class UserCreateForm(Form):
            user_name = TextField(
                _(u'User name'), 
                [
                    validators.Required(self.required_msg),
                ]
            )
            display_name = TextField(_(u'Display name'), [])
            password = PasswordField(
                _(u'Password'), 
                [
                    validators.Required(self.required_msg),
                    similar('user_name', self.password_too_similar_msg),
                    similar('display_name', self.password_too_similar_msg),
                    validators.Length(min=6)
                ]
            )
            email = TextField(
                _(u'Email'), 
                [
                    validators.Email(self.invalid_email_msg)
                ]
            )
            groups = SelectMultipleField(_(u'Groups'), widget=CheckboxList())
        return UserCreateForm
    
    def make_user_edit_form(self):
        _ = self.localizer
        
        class UserEditForm(Form):
            display_name = TextField(_(u'Display name'), [])
            password = PasswordField(
                _(u'Password'), 
                [
                    #similar('user_name', self.password_too_similar_msg),
                    # TODO: check is password similar to user_name here
                    # validators.Length(min=6)
                ]
            )
            email = TextField(
                _(u'Email'), [
                    validators.Email(self.invalid_email_msg)
                ]
            )
            groups = SelectMultipleField(_(u'Groups'), widget=CheckboxList())
        return UserEditForm
    
    def make_group_create_form(self):
        _ = self.localizer
        
        class GroupCreateForm(Form):
            group_name = TextField(
                _(u'Group name'), [
                    validators.Required(self.required_msg),
                ]
            )
            display_name = TextField(_(u'Display name'), [])
            permissions = SelectMultipleField(
                _(u'Permissions'), 
                widget=CheckboxList()
            )
        return GroupCreateForm
    
    def make_group_edit_form(self):
        _ = self.localizer
        
        class GroupEditForm(Form):
            group_name = TextField(
                _(u'Group name'), 
                [
                    validators.Required(self.required_msg),
                ]
            )
            display_name = TextField(_(u'Display name'), [])
            permissions = SelectMultipleField(
                _(u'Permissions'), 
                widget=CheckboxList()
            )
        return GroupEditForm
    
    def make_permission_create_form(self):
        _ = self.localizer
        
        class PermissionCreateForm(Form):
            permission_name = TextField(
                _(u'Permission name'), 
                [
                    validators.Required(self.required_msg),
                ]
            )
            description = TextField(_(u'Description'), [])
        return PermissionCreateForm
    
    def make_permission_edit_form(self):
        _ = self.localizer
        
        class PermissionEditForm(Form):
            permission_name = TextField(
                _(u'Permission name'), 
                [
                    validators.Required(self.required_msg),
                ]
            )
            description = TextField(_(u'Description'), [])
        return PermissionEditForm
