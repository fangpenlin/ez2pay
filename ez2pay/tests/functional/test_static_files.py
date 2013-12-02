from __future__ import unicode_literals

from .helper import ViewTestCase


class TestStaticFiles(ViewTestCase):
    def test_home(self):
        self.testapp.get('/favicon.ico', status=200)
