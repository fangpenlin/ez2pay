from __future__ import unicode_literals
import os
import unittest
import datetime


def create_session():
    """Create engine and session, return session then
    
    """
    from pyramid.settings import asbool
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker
    from zope.sqlalchemy import ZopeTransactionExtension
    from ez2pay.models.tables import DeclarativeBase 

    echo_sql = asbool(os.environ.get('TEST_ECHO_SQL', False))
    
    engine = create_engine('sqlite:///', convert_unicode=True, echo=echo_sql)
    DeclarativeBase.metadata.bind = engine
    DeclarativeBase.metadata.create_all()

    session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        extension=ZopeTransactionExtension()
    ))
    return session


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        from ez2pay.models import tables
        self.session = create_session()
        self._old_now_func = tables.set_now_func(datetime.datetime.utcnow)

    def tearDown(self):
        from ez2pay.models import tables
        self.session.remove()
        tables.DeclarativeBase.metadata.drop_all()
        tables.set_now_func(self._old_now_func)
