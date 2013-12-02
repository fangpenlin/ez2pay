# -*- coding: utf8 -*-
from __future__ import unicode_literals

import transaction

from .helper import ViewTestCase


class TestAccountView(ViewTestCase):
    def setUp(self):
        super(TestAccountView, self).setUp()
        from ez2pay.models.user import UserModel
        model = UserModel(self.testapp.session)
        with transaction.manager:
            model.create(
                user_name='tester', 
                display_name='tester', 
                password='testerpass', 
                email='tester@example.com'
            )
        
    def login_user(self, username_or_email='tester', password='testerpass'):
        """Login as user and return cookie
        
        """
        params = dict(
            username_or_email=username_or_email, 
            password=password
        )
        self.testapp.post('/login', params)
        
    def assert_login_success(self, name, password):
        """Assert login success
        
        """
        params = dict(
            username_or_email=name, 
            password=password
        )
        self.testapp.post('/login', params, status='3*')
        
    def assert_login_failed(self, name, password):
        """Assert login failed
        
        """
        params = dict(
            username_or_email=name, 
            password=password
        )
        self.testapp.post('/login', params, status=200)
        
    def test_login(self):
        self.testapp.get('/login', status=200)
        # test valid login
        self.assert_login_success('tester', 'testerpass')
        self.assert_login_success('TESTER', 'testerpass')
        self.assert_login_success('TeStEr', 'testerpass')
        self.assert_login_success('tester@example.com', 'testerpass')
        self.assert_login_success('TESTER@example.com', 'testerpass')
        self.assert_login_success('TESTER@Example.Com', 'testerpass')
        
    def test_login_fail(self):
        self.testapp.get('/login', status=200)
        
        with self.assertRaises(Exception):
            self.assert_login_failed('tester', 'testerpass')
        
        # test invalid login
        self.assert_login_failed('', '')
        self.assert_login_failed('tester', 'tester')
        self.assert_login_failed('tester', 'TESTERPASS')
        self.assert_login_failed('tester', 'TeStErPaSs')
        self.assert_login_failed('tester@example.com', 'tester')
        self.assert_login_failed('tester@example.com', 'TESTERPASS')
        self.assert_login_failed('tester@example.com', 'TeStErPaSs')
        self.assert_login_failed('tester', '')
        self.assert_login_failed('tester@example.com', '')
        self.assert_login_failed('abc', '123')
        self.assert_login_failed('not_exist@example.com', '123')
        self.assert_login_failed('not_exist@example.com', '')
        
    def test_logout(self):
        # try to logout when not logged in
        self.testapp.get('/logout', status=400)
        self.login_user('tester', 'testerpass')
        self.testapp.get('/logout', status='3*')

    def test_recovery_password(self):
        self.testapp.get('/forgot_password', status=200)

        res = self.testapp.post('/forgot_password', dict(
            email='tester@example.com',
        ), status=200)
        mailer = res.request.environ['pyramid_mailer.dummy_mailer']
        self.assertEqual(len(mailer.outbox), 1)
        mail = mailer.outbox[0]
        # find recovery link
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(mail.html)
        links = soup.findAll('a')
        recovery_link = None
        for link in links:
            if 'recovery_password' in link['href']:
                recovery_link = link['href']
                break

        self.testapp.get('/recovery_password?user_name=xxx&code=xxx', status=404)
        self.testapp.get('/recovery_password?user_name=tester&code=xxx', status=403)
        self.testapp.get(recovery_link, status=200)

        import urlparse
        import urllib
        q = urlparse.parse_qs(recovery_link.split('?')[-1])

        code = q['code'][0]
        qs = q.copy()
        qs.update(dict(code=code + '0'))
        qs = urllib.urlencode(qs, True)
        self.testapp.get('/recovery_password?' + qs, status=403)

        qs = q.copy()
        qs.update(dict(user_name='tester01'))
        qs = urllib.urlencode(qs, True)
        self.testapp.get('/recovery_password?' + qs, status=404)

        self.testapp.get(recovery_link, status=200)
        self.testapp.post(recovery_link, dict(
            new_password_confirm='password1',
            new_password='password2',
        ), status=200) 
        # make sure the password is not changed
        self.assert_login_success('tester', 'testerpass')

        self.testapp.post(recovery_link, dict(
            new_password_confirm='newpass',
            new_password='newpass',
        ), status=302) 
        # make sure the password is not changed
        self.assert_login_success('tester', 'newpass')

    def assert_register_form_error(self, params):
        res = self.testapp.post('/register', params, status=200)
        errors = res.html.findAll('span', {'class': 'field_error'})
        self.assert_(len(errors) > 0)

    def assert_register_success(self, params):
        from ez2pay.models.user import UserModel
        res = self.testapp.post('/register', params, status=302)

        model = UserModel(self.testapp.session)
        user = model.get_by_name(params['user_name'])
        self.assertNotEqual(user, None)
        self.assertEqual(user.user_name, params['user_name'])
        self.assertEqual(user.email, params['email'])
        self.assertEqual(user.email, params['email_confirm'])
        self.assertEqual(user.verified, False)
        self.assertNotEqual(user.password, params['password'])
        self.assertNotIn(params['password'], user.password)
        return res

    def get_csrf_token(self, res):
        input = res.html.find('input', dict(name='csrf_token'))
        self.assert_(input)
        return input['value']

    def test_register(self):
        res = self.testapp.get('/register', status=200)
        csrf_token = self.get_csrf_token(res)

        self.assert_register_success(dict(
            csrf_token=csrf_token, 
            user_name='tester2',
            email='tester2@example.com',
            email_confirm='tester2@example.com',
            password='testpass',
            terms_of_service='1',
        ))

        # empty form
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='',
            email='',
            email_confirm='',
            password='',
            terms_of_service='1',
        ))
        # missing user name
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='',
            email='tester@example.com',
            email_confirm='tester@example.com',
            password='testpass',
            terms_of_service='1',
        ))
        # missing email
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='tester2',
            email='',
            email_confirm='',
            password='testpass',
            terms_of_service='1',
        ))
        # not match email
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='tester2',
            email='tester1@example.com',
            email_confirm='tester2@example.com',
            password='testpass',
            terms_of_service='1',
        ))
        # duplicated user name
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='tester',
            email='tester@example.com',
            email_confirm='tester@example.com',
            password='testpass',
            terms_of_service='1',
        ))
        # did not accept the terms
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='tester3',
            email='tester3@example.com',
            email_confirm='tester3@example.com',
            password='testpass',
        ))
        # bad username 
        self.assert_register_form_error(dict(
            csrf_token=csrf_token, 
            user_name='&&&',
            email='tester@example.com',
            email_confirm='tester@example.com',
            password='testpass',
            terms_of_service='1',
        ))

    def test_activate(self):
        from ez2pay.models.user import UserModel
        res = self.testapp.get('/register', status=200)
        csrf_token = self.get_csrf_token(res)

        res = self.assert_register_success(dict(
            csrf_token=csrf_token, 
            user_name='tester2',
            email='tester2@example.com',
            email_confirm='tester2@example.com',
            password='testpass',
            terms_of_service='1',
        ))
        mailer = res.request.environ['pyramid_mailer.dummy_mailer']
        self.assertEqual(len(mailer.outbox), 1)
        self.assertIn('activation', mailer.outbox[0].subject)
        mail = mailer.outbox[0]

        # find activation link
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(mail.html)
        links = soup.findAll('a')
        activate_link = None
        for link in links:
            if 'activate' in link['href']:
                activate_link = link['href']
                break
        self.assertNotEqual(activate_link, None)
        code = activate_link.split('/')[-1]

        self.testapp.get('/activate/tester2/badcode', status=403)
        self.testapp.get('/activate/tester2/' + code + 'x', status=403)
        self.testapp.get('/activate/tester2/' + code[:-1] + 'x', status=403)

        model = UserModel(self.testapp.session)
        user = model.get_by_name('tester2')
        self.assertEqual(user.verified, False)

        self.testapp.get('/activate/tester2/' + code, status=200)
        user = model.get_by_name('tester2')
        self.assertEqual(user.verified, True)
