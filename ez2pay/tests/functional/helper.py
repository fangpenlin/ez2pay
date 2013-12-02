from __future__ import unicode_literals
import os
import unittest


class ViewTestCase(unittest.TestCase):
    
    def setUp(self):
        from webtest import TestApp
        from ez2pay import main
        from ez2pay.models import setup_database
        from ez2pay.models.tables import DeclarativeBase

        if hasattr(self, 'settings'):
            settings = self.settings
        else:
            settings = dict(use_dummy_mailer=True)

        # init database
        db_url = os.environ.get('FUNC_TEST_DB', 'sqlite://')
        settings['sqlalchemy.url'] = db_url
        settings = setup_database({}, **settings)
        DeclarativeBase.metadata.bind = settings['engine']
        DeclarativeBase.metadata.create_all()

        app = main({}, **settings)
        self.testapp = TestApp(app)
        self.testapp.session = settings['session']

    def tearDown(self):
        from ez2pay.models.tables import DeclarativeBase
        self.testapp.session.remove()
        DeclarativeBase.metadata.drop_all()
