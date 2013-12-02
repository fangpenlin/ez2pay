from __future__ import unicode_literals
import os
import unittest
import tempfile

from flexmock import flexmock


class TestUtils(unittest.TestCase):
        
    def test_check_csrf_token(self):
        from pyramid.httpexceptions import HTTPBadRequest
        from ez2pay.utils import check_csrf_token

        mock_session = (
            flexmock()
            .should_receive('get_csrf_token')
            .replace_with(lambda: 'MOCK_CSRF_TOKEN')
            .twice()
            .mock()
        )

        mock_request = flexmock(
            session=mock_session,
            params=dict(csrf_token='MOCK_CSRF_TOKEN')
        )

        check_csrf_token(mock_request)

        mock_request = flexmock(
            session=mock_session,
            params=dict(csrf_token='BAD_TOKEN')
        )
        with self.assertRaises(HTTPBadRequest):
            check_csrf_token(mock_request)

    def test_generate_random_code(self):
        from ez2pay.utils import generate_random_code
        times = 1000
        codes = [generate_random_code() for _ in range(times)]
        self.assertEqual(len(set(codes)), times)

    def test_load_app_cfg(self):
        import textwrap
        from ez2pay.utils import load_app_cfg
        # make sure the configuration is loaded correctly
        cfg = load_app_cfg()
        self.assertTrue(cfg)

        temp = tempfile.NamedTemporaryFile()

        temp.write(textwrap.dedent("""\
        ---
        mock_key: mock_value
        ...
        """))
        temp.flush()

        os.environ['APP_CFG_PATH'] = temp.name
        cfg = load_app_cfg()
        self.assertEqual(cfg, dict(mock_key='mock_value'))
