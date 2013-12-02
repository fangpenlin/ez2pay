from __future__ import unicode_literals

import transaction
from pyramid.view import view_config
from pyramid.security import Allow
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from ez2pay.i18n import LocalizerFactory
from ez2pay.models.user import UserModel
from ez2pay.models.group import GroupModel
from ez2pay.models.permission import PermissionModel
from ez2pay.utils import check_csrf_token
from .forms import FormFactory

get_localizer = LocalizerFactory()


class AdminContext(object):
    """Context for providing ACL attribute of administrator
    
    """
    
    # only users who have manage permission can access
    __acl__ = [
        (Allow, 'permission:admin', 'admin'),
    ]
    
    def __init__(self, request):
        pass


@view_config(route_name='admin.home', 
             renderer='templates/home.genshi',
             permission='admin')
def home(request):
    return dict()


@view_config(route_name='admin.user_list', 
             renderer='templates/user_list.genshi',
             permission='admin')
def user_list(request):
    user_model = UserModel(request.db_session)
    users = user_model.get_list()
    return dict(users=users)


@view_config(route_name='admin.user_create', 
             renderer='templates/user_create.genshi',
             permission='admin')
def user_create(request):
    _ = get_localizer(request)
    
    user_model = UserModel(request.db_session)
    group_model = GroupModel(request.db_session)
    
    factory = FormFactory(_)
    UserCreateForm = factory.make_user_create_form()
    form = UserCreateForm(request.params)
    
    groups = group_model.get_list()
    form.groups.choices = [
        (str(g.group_id), '%s - %s' % (g.group_name, g.display_name)) 
        for g in groups
    ]
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        user_name = request.params['user_name']
        display_name = request.params['display_name']
        password = request.params['password']
        email = request.params['email']
        groups = request.params.getall('groups')
        
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
                    display_name=display_name,
                    password=password,
                    email=email,
                )
                user_model.update_groups(user_id, map(int, groups))
            
            msg = _(u"User ${user_name} has been created", 
                    mapping=dict(user_name=user_name))
            request.add_flash(msg, 'success')
            return HTTPFound(location=request.route_url('admin.user_list'))
    
    return dict(form=form)


@view_config(route_name='admin.user_edit', 
             renderer='templates/user_edit.genshi',
             permission='admin')
def user_edit(request):
    _ = get_localizer(request)
    
    user_model = UserModel(request.db_session)
    group_model = GroupModel(request.db_session)
    
    user_name = request.matchdict['user_name']
    user = user_model.get_by_name(user_name)
    if user is None:
        msg = _(u'User %s does not exists') % user_name
        return HTTPNotFound(msg)
    user_groups = [str(g.group_id) for g in user.groups]
    
    factory = FormFactory(_)
    UserEditForm = factory.make_user_edit_form()
    form = UserEditForm(
        request.params, 
        display_name=user.display_name,
        email=user.email,
        groups=user_groups
    )
    
    groups = group_model.get_list()
    form.groups.choices = [
        (str(g.group_id), '%s - %s' % (g.group_name, g.display_name), ) 
        for g in groups
    ]
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        display_name = request.params['display_name']
        password = request.params['password']
        email = request.params['email']
        groups = request.params.getall('groups')
        
        by_email = user_model.get_by_email(email)
        if by_email is not None and email != user.email:
            msg = _(u'Email %s already exists') % email
            form.email.errors.append(msg)
            validate_result = False
        
        if validate_result:
            with transaction.manager:
                user_model.update_user(
                    user_id=user.user_id,
                    display_name=display_name,
                    email=email,
                )
                if password:
                    user_model.update_password(user.user_id, password)
                user_model.update_groups(user.user_id, map(int, groups))
            
            msg = _(u"User ${user_name} has been updated", 
                    mapping=dict(user_name=user_name))
            request.add_flash(msg, 'success')
            url = request.route_url('admin.user_edit', 
                                    user_name=user.user_name)
            return HTTPFound(location=url)
    
    return dict(form=form, user=user)


@view_config(route_name='admin.group_list', 
             renderer='templates/group_list.genshi',
             permission='admin')
def group_list(request):
    group_model = GroupModel(request.db_session)
    groups = group_model.get_list()
    return dict(groups=groups)


@view_config(route_name='admin.group_create', 
             renderer='templates/group_create.genshi',
             permission='admin')
def group_create(request):
    _ = get_localizer(request)
    
    group_model = GroupModel(request.db_session)
    permission_model = PermissionModel(request.db_session)
    
    factory = FormFactory(_)
    GroupCreateForm = factory.make_group_create_form()
    form = GroupCreateForm(request.params)
    
    permissions = permission_model.get_list()
    form.permissions.choices = [
        (str(p.permission_id), p.permission_name) 
        for p in permissions
    ]
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        group_name = request.params['group_name']
        display_name = request.params['display_name']
        permissions = request.params.getall('permissions')
        
        by_name = group_model.get_by_name(group_name)
        if by_name is not None:
            msg = _(u'Group name %s already exists') % group_name
            form.group_name.errors.append(msg)
            validate_result = False

        if validate_result:
            with transaction.manager:
                group_id = group_model.create(
                    group_name=group_name, 
                    display_name=display_name, 
                )
                group_model.update_permissions(
                    group_id=group_id, 
                    permission_ids=permissions,
                )
            
            msg = _(u"Group ${group_name} has been created", 
                    mapping=dict(group_name=group_name))
            request.add_flash(msg, 'success')
            return HTTPFound(location=request.route_url('admin.group_list'))
    
    return dict(form=form)


@view_config(route_name='admin.group_edit', 
             renderer='templates/group_edit.genshi',
             permission='admin')
def group_edit(request):
    _ = get_localizer(request)
    
    group_model = GroupModel(request.db_session)
    permission_model = PermissionModel(request.db_session)
    
    group_name = request.matchdict['group_name']
    group = group_model.get_by_name(group_name)
    if group is None:
        msg = _(u'Group %s does not exist') % group_name
        return HTTPNotFound(msg)
    group_permissions = [str(p.permission_id) for p in group.permissions]
    
    factory = FormFactory(_)
    GroupEditForm = factory.make_group_edit_form()
    form = GroupEditForm(
        request.params,
        permissions=group_permissions,
        group_name=group.group_name,
        display_name=group.display_name
    )
    
    permissions = permission_model.get_list()
    form.permissions.choices = [
        (str(p.permission_id), p.permission_name) 
        for p in permissions
    ]
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        group_name = request.params['group_name']
        display_name = request.params['display_name']
        permissions = request.params.getall('permissions')
        
        by_name = group_model.get_by_name(group_name)
        if by_name is not None and group_name != group.group_name:
            msg = _(u'Group name %s already exists') % group_name
            form.group_name.errors.append(msg)
            validate_result = False

        if validate_result:
            with transaction.manager:
                group_model.update_group(
                    group_id=group.group_id,
                    group_name=group_name, 
                    display_name=display_name, 
                )
                group_model.update_permissions(
                    group_id=group.group_id, 
                    permission_ids=permissions,
                )
            group = group_model.get(group.group_id)
            msg = _(u"Group ${group_name} has been updated", 
                    mapping=dict(group_name=group.group_name))
            request.add_flash(msg, 'success')
            url = request.route_url('admin.group_edit', 
                                    group_name=group.group_name)
            return HTTPFound(location=url)
    
    return dict(form=form, group=group)


@view_config(route_name='admin.permission_list', 
             renderer='templates/permission_list.genshi',
             permission='admin')
def permission_list(request):
    permission_model = PermissionModel(request.db_session)
    permissions = permission_model.get_list()
    return dict(permissions=permissions)


@view_config(route_name='admin.permission_create', 
             renderer='templates/permission_create.genshi',
             permission='admin')
def permission_create(request):
    _ = get_localizer(request)
    
    permission_model = PermissionModel(request.db_session)
    
    factory = FormFactory(_)
    PermissionCreateForm = factory.make_permission_create_form()
    form = PermissionCreateForm(request.params)
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        permission_name = request.params['permission_name']
        description = request.params['description']
        
        by_name = permission_model.get_by_name(permission_name)
        if by_name is not None:
            msg = _(u'Permission name %s already exists') % permission_name
            form.permission_name.errors.append(msg)
            validate_result = False

        if validate_result:
            with transaction.manager:
                permission_model.create(
                    permission_name=permission_name, 
                    description=description, 
                )
            
            msg = _(u"Permission ${permission_name} has been created", 
                    mapping=dict(permission_name=permission_name))
            request.add_flash(msg, 'success')
            return HTTPFound(location=request.route_url('admin.permission_list'))
    return dict(form=form)


@view_config(route_name='admin.permission_edit', 
             renderer='templates/permission_edit.genshi',
             permission='admin')
def permission_edit(request):
    _ = get_localizer(request)
    
    permission_model = PermissionModel(request.db_session)
    
    permission_name = request.matchdict['permission_name']
    permission = permission_model.get_by_name(permission_name)
    if permission is None:
        msg = _(u'Permission %s does not exist') % permission_name
        return HTTPNotFound(msg)
    
    factory = FormFactory(_)
    PermissionEditForm = factory.make_permission_edit_form()
    form = PermissionEditForm(request.params, permission)
    
    if request.method == 'POST':
        check_csrf_token(request)
        
        validate_result = form.validate()
        permission_name = request.params['permission_name']
        description = request.params['description']
        
        by_name = permission_model.get_by_name(permission_name)
        if (
            by_name is not None and 
            permission_name != permission.permission_name
        ):
            msg = _(u'Permission name %s already exists') % permission_name
            form.permission_name.errors.append(msg)
            validate_result = False

        if validate_result:
            with transaction.manager:
                permission_model.update_permission(
                    permission_id=permission.permission_id,
                    permission_name=permission_name, 
                    description=description, 
                )
            
            msg = _(u"Permission ${permission_name} has been updated", 
                    mapping=dict(permission_name=permission_name))
            request.add_flash(msg, 'success')
            url = request.route_url('admin.permission_edit', 
                                    permission_name=permission_name)
            return HTTPFound(location=url)
        
    return dict(form=form, permission=permission)
