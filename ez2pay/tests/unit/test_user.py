from __future__ import unicode_literals

from .helper import ModelTestCase

import transaction


class TestUserModel(ModelTestCase):
        
    def make_one(self):
        from ez2pay.models.user import UserModel
        return UserModel(self.session)
    
    def make_group_model(self):
        from ez2pay.models.group import GroupModel
        return GroupModel(self.session)
    
    def test_create_user(self):
        model = self.make_one()
        
        user_name = 'victorlin'
        email = 'bornstub@gmail.com'
        display_name = user_name
        password = 'thepass'
        
        with transaction.manager:
            user_id = model.create(
                user_name=user_name,
                email=email,
                display_name=display_name,
                password=password,
            )
        user = model.get(user_id)
        
        self.assertEqual(user.user_name, user_name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.display_name, display_name)
        
        # make sure the password is not in plain form
        self.assertNotEqual(user.password, password)
        self.assertNotIn(password, user.password)
        
    def test_authenticate_user(self):
        model = self.make_one()
        with transaction.manager:
            user_1 = model.create(
                user_name=u'tester',
                email=u'tester@now.in',
                display_name=u'tester',
                password=u'first_pass'
            )
            user_2 = model.create(
                user_name=u'tester2',
                email=u'tester2@now.in',
                display_name=u'tester2',
                password=u'pass2'
            )
            user_3 = model.create(
                user_name=u'tester3',
                email=u'tester3@now.in',
                display_name=u'tester2',
                password=u'tester3_PaSs3'
            )
        
        # cases should pass
        result = model.authenticate_user(u'tester', u'first_pass')
        self.assertEqual(result, user_1)
        result = model.authenticate_user(u'tester@now.in', u'first_pass')
        self.assertEqual(result, user_1)
        
        result = model.authenticate_user(u'tester2', u'pass2')
        self.assertEqual(result, user_2)
        result = model.authenticate_user(u'TeStEr2', u'pass2')
        self.assertEqual(result, user_2)
        result = model.authenticate_user(u'tester2@now.in', u'pass2')
        self.assertEqual(result, user_2)
        result = model.authenticate_user(u'TESTER2@now.in', u'pass2')
        self.assertEqual(result, user_2)
        result = model.authenticate_user(u'TeSTer2@now.in', u'pass2')
        self.assertEqual(result, user_2)
        
        result = model.authenticate_user(u'tester3', u'tester3_PaSs3')
        self.assertEqual(result, user_3)
        result = model.authenticate_user(u'tester3@now.in', u'tester3_PaSs3')
        self.assertEqual(result, user_3)
        
        # cases should not pass
        from ez2pay.models.user import BadPassword
        from ez2pay.models.user import UserNotExist
        
        with self.assertRaises(BadPassword):
            model.authenticate_user(u'tester@now.in', u'First_pass')
        with self.assertRaises(BadPassword):
            model.authenticate_user(u'tester@now.in', u'First_Pass')
        with self.assertRaises(BadPassword):
            model.authenticate_user(u'tester@now.in', u'abcd')
        with self.assertRaises(BadPassword):
            model.authenticate_user(u'tester@now.in', u'')
        with self.assertRaises(BadPassword):
            model.authenticate_user(u'tester2@now.in', u'abc')
        with self.assertRaises(UserNotExist):
            model.authenticate_user(u'user_not_exist', u'abc')
            
        # make sure not activated user can't not login
        model.create(
            user_name=u'not_activated',
            email=u'not_activated@now.in',
            display_name=u'not_activated',
            password=u'not_activated'
        )
        
    def test_get_user(self):
        model = self.make_one()
        
        user_name = 'victorlin'
        email = 'bornstub@gmail.com'
        display_name = user_name
        password = 'thepass'
        
        with transaction.manager:
            user_id = model.create(
                user_name=user_name,
                email=email,
                display_name=display_name,
                password=password,
            )
            user_id2 = model.create(
                user_name='user2',
                email='user2@example.com',
                display_name='user2',
                password='user2pass',
            )
        user = model.get(user_id)
        self.assertEqual(user.user_id, user_id)
        
        user = model.get_by_email(email)
        self.assertEqual(user.user_id, user_id)
        
        users = list(model.get_list(ids=[user_id]))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].user_id, user_id)
        
        user = model.get(user_id2)
        self.assertEqual(user.user_id, user_id2)
        
        user = model.get_by_email('user2@example.com')
        self.assertEqual(user.user_id, user_id2)
        
    def test_update_groups(self):
        model = self.make_one()
        group_model = self.make_group_model()
        
        user_name = 'victorlin'
        email = 'bornstub@gmail.com'
        display_name = user_name
        password = 'thepass'
        
        with transaction.manager:
            user_id = model.create(
                user_name=user_name,
                email=email,
                display_name=display_name,
                password=password,
            )
            gid1 = group_model.create('g1')
            gid2 = group_model.create('g2')
            gid3 = group_model.create('g3')
            
        user = model.get(user_id)
        gids = set([g.group_id for g in user.groups])
        self.assertEqual(gids, set([]))
        
        def assert_update(new_groups):
            with transaction.manager:
                model.update_groups(user_id, new_groups)
            user = model.get(user_id)
            gids = set([g.group_id for g in user.groups])
            self.assertEqual(gids, set(new_groups))
            
        assert_update([gid1])
        assert_update([gid1, gid2])
        assert_update([gid1, gid2, gid3])
        assert_update([gid1, gid3])
        assert_update([gid3])
        assert_update([])
