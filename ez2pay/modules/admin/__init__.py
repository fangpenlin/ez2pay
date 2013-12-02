from __future__ import unicode_literals


def includeme(config):
    def add_route(route_name, path):
        config.add_route(
            route_name, path,
            factory='ez2pay.modules.admin.views.AdminContext'
        )
    add_route('admin.home', '/')
    
    # user
    add_route('admin.user_list', '/user/list')
    add_route('admin.user_create', '/user/create')
    add_route('admin.user_edit', '/user/edit/{user_name}')
    
    # group
    add_route('admin.group_list', '/group/list')
    add_route('admin.group_create', '/group/create')
    add_route('admin.group_edit', '/group/edit/{group_name}')
    
    # permission
    add_route('admin.permission_list', '/permission/list')
    add_route('admin.permission_create', '/permission/create')
    add_route('admin.permission_edit', '/permission/edit/{permission_name}')
