# -*- coding: utf8 -*-
from __future__ import unicode_literals

from .helper import ViewTestCase

import transaction


class TestAdminView(ViewTestCase):
    def setUp(self):
        super(TestAdminView, self).setUp()
        from ez2pay.models.user import UserModel
        from ez2pay.models.group import GroupModel
        from ez2pay.models.permission import PermissionModel
        user_model = UserModel(self.testapp.session)
        group_model = GroupModel(self.testapp.session)
        permission_model = PermissionModel(self.testapp.session)
        with transaction.manager:
            user_model.create(
                user_name='tester', 
                display_name='tester', 
                password='testerpass', 
                email='tester@example.com'
            )
            admin_id = user_model.create(
                user_name='admin', 
                display_name='admin', 
                password='adminpass', 
                email='admin@example.com'
            )
            group_id = group_model.create(
                group_name='admin', 
                display_name='admin', 
            )
            permission_id = permission_model.create(
                permission_name='admin', 
                description='admin'
            )
            group_model.update_permissions(group_id, [permission_id])
            user_model.update_groups(admin_id, [group_id])
        
    def login_user(self, username_or_email='tester', password='testerpass'):
        """Login as user and return cookie
        
        """
        params = dict(
            username_or_email=username_or_email, 
            password=password
        )
        self.testapp.post('/login', params)
        
    def logout(self):
        self.testapp.get('/logout')
        
    def assert_access_success(self, name, password):
        """Assert login success
        
        """
        params = dict(
            username_or_email=name, 
            password=password
        )
        self.testapp.post('/login', params, status='3*')
        
    def assert_access(self, url, result):
        """Assert login failed
        
        """
        res = self.testapp.get(url, status=200)
        # we should find login form in the page
        found = False
        for form in res.forms.itervalues():
            if form.action.endswith('/login'):
                found = True
                break
        self.assertEqual(not found, result)
    
    def test_access(self):
        def assert_access_all(result):
            self.assert_access('/admin/', result)
            
            self.assert_access('/admin/user/list', result)
            self.assert_access('/admin/user/create', result)
            self.assert_access('/admin/user/edit/tester', result)
            
            self.assert_access('/admin/group/list', result)
            self.assert_access('/admin/group/create', result)
            self.assert_access('/admin/group/edit/admin', result)
            
            self.assert_access('/admin/permission/list', result)
            self.assert_access('/admin/permission/create', result)
            self.assert_access('/admin/permission/edit/admin', result)
        
        assert_access_all(False)
        self.login_user('tester', 'testerpass')
        assert_access_all(False)
        self.login_user('admin', 'adminpass')
        assert_access_all(True)
        self.login_user('tester', 'testerpass')
        assert_access_all(False)
        self.login_user('admin', 'adminpass')
        assert_access_all(True)
        self.logout()
        assert_access_all(False)
