from __future__ import unicode_literals
import os
import hmac

import yaml
from pyramid.httpexceptions import HTTPBadRequest


def check_csrf_token(request):
    token = request.session.get_csrf_token()
    if token != request.params['csrf_token']:
        raise HTTPBadRequest('CSRF token did not match')


def generate_random_code():
    """Generate random code
    
    """
    random_code = os.urandom(60)
    return hmac.new(random_code).hexdigest()


def load_app_cfg():
    """Load application configuration and return
    
    """
    import ez2pay
    app_dir = os.path.abspath(os.path.dirname(ez2pay.__file__))
    app_dir, _ = os.path.split(app_dir)
    app_cfg_path = os.path.join(app_dir, 'app_cfg.yaml')
    app_cfg_env = 'APP_CFG_PATH'
    if app_cfg_env in os.environ:
        app_cfg_path = os.environ[app_cfg_env]
    with open(app_cfg_path, 'rt') as f:
        app_cfg = yaml.load(f)
    return app_cfg
