from __future__ import unicode_literals

from .helper import ViewTestCase


class TestFrontPagesView(ViewTestCase):
    def test_home(self):
        self.testapp.get('/', status=200)

    def test_terms_of_service(self):
        self.testapp.get('/terms_of_service', status=200)

    def test_contact_us_received(self):
        self.testapp.get('/contact_us_received', status=200)

    def test_contact_us(self):
        self.testapp.get('/contact_us', status=200)

        res = self.testapp.post('/contact_us', dict(
            email='homura@qb-inc.com',
            content='I love Madoka',
        ), status=302)
        mailer = res.request.environ['pyramid_mailer.dummy_mailer']
        self.assertEqual(len(mailer.outbox), 1)
        self.assertIn('contacts mail', mailer.outbox[0].subject)
        self.assertIn('I love Madoka', mailer.outbox[0].body)
