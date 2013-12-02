from __future__ import unicode_literals
import os
import sys
import unittest
import tempfile
import shutil
import textwrap
import sqlite3
import StringIO


class TestInitializedb(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_usage(self):
        from ez2pay.scripts import initializedb

        filename = '/path/to/initializedb'

        old_stdout = sys.stdout
        usage_out = StringIO.StringIO()
        sys.stdout = usage_out
        try:
            with self.assertRaises(SystemExit):
                initializedb.main([filename])
        finally:
            sys.stdout = old_stdout
        expected = textwrap.dedent("""\
        usage: initializedb <config_uri>
        (example: "initializedb development.ini")
        """)
        self.assertMultiLineEqual(usage_out.getvalue(), expected)

    def test_main(self):
        from ez2pay.scripts import initializedb

        def mock_raw_input(text):
            return 'tester@example.com'

        def mock_getpass(text):
            return 'testerpass'

        cfg_path = os.path.join(self.temp_dir, 'config.ini')
        with open(cfg_path, 'wt') as f:
            f.write(textwrap.dedent("""\
            [app:main]
            use = egg:ez2pay

            sqlalchemy.url = sqlite:///%(here)s/ez2pay.sqlite
            """))
        initializedb.main(
            [initializedb.__file__, cfg_path],
            input_func=mock_raw_input,
            getpass_func=mock_getpass,
        )

        sqlite_path = os.path.join(self.temp_dir, 'ez2pay.sqlite')
        self.assertTrue(os.path.exists(sqlite_path))

        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertEqual(set(tables), set([
            'user',
            'user_group',
            'group',
            'group_permission',
            'permission',
        ]))

        # TODO: do more checks here
