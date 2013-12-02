from __future__ import unicode_literals

from .helper import ModelTestCase

import transaction


class TestAuth(ModelTestCase):

    def make_user_model(self):
        from ez2pay.models.user import UserModel
        return UserModel(self.session)

    def make_group_model(self):
        from ez2pay.models.group import GroupModel 
        return GroupModel(self.session)
 
    def make_permission_model(self):
        from ez2pay.models.permission import PermissionModel 
        return PermissionModel(self.session)

    def test_get_group(self):
        from pyramid.testing import DummyRequest
        from ez2pay.auth import get_group

        user_model = self.make_user_model()
        group_model = self.make_group_model()
        permission_model = self.make_permission_model()
        
        with transaction.manager:
            user_id1 = user_model.create(
                user_name='tester1',
                email='tester1@example.com',
                display_name='tester1',
                password='thepass',
            )
            user_id2 = user_model.create(
                user_name='tester2',
                email='tester2@example.com',
                display_name='tester2',
                password='thepass',
            )
            user_id3 = user_model.create(
                user_name='tester3',
                email='tester3@example.com',
                display_name='tester3',
                password='thepass',
            )
            group_id1 = group_model.create(
                group_name='super_users',
                display_name='Super user',
            )
            group_id2 = group_model.create(
                group_name='guest',
                display_name='Guest group',
            )
            permission_id1 = permission_model.create(
                permission_name='admin',
                description='Admin',
            )
            permission_id2 = permission_model.create(
                permission_name='manager',
                description='Manager',
            )
            permission_id3 = permission_model.create(
                permission_name='guest',
                description='Guest',
            )

            # + group1 super_users
            #     + permission1 admin 
            #     + permission2 manager 
            group_model.update_permissions(
                group_id1, 
                [permission_id1, permission_id2]
            )
            # + group2 guest
            #     + permission3 guest
            group_model.update_permissions(group_id2, [permission_id3])

            # user1
            #     + group1 super_users
            #         + permission1 admin 
            #         + permission2 manager 
            user_model.update_groups(user_id1, [group_id1])
            # user2
            #     + group2 guest
            #         + permission3 guest 
            user_model.update_groups(user_id2, [group_id2])
            # user3
            #     (nothing)

        mock_request = DummyRequest()
        mock_request.db_session = self.session

        def assert_group(user_id, expected):
            group = get_group(user_id, mock_request)
            self.assertEqual(group, set(expected))

        assert_group(
            user_id1, 
            [
                'user', 
                'user:tester1',
                'group:super_users',
                'permission:admin',
                'permission:manager',
            ]
        )
        assert_group(
            user_id2, 
            [
                'user', 
                'user:tester2',
                'group:guest',
                'permission:guest',
            ]
        )
        assert_group(
            user_id3, 
            [
                'user', 
                'user:tester3',
            ]
        )
        # not exist user
        assert_group(999, [])
        assert_group(None, [])
