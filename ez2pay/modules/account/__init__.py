from __future__ import unicode_literals


def includeme(config):
    config.add_route('account.login', '/login')
    config.add_route('account.logout', '/logout')
    config.add_route('account.register', '/register')
    config.add_route('account.check_mailbox', '/check_mailbox')
    config.add_route('account.activate', '/activate/{user_name}/{code}')
    config.add_route('account.forgot_password', '/forgot_password')
    config.add_route('account.recovery_password', '/recovery_password')
