from __future__ import unicode_literals

#: type of messages
MSG_TYPES = [
    'info',
    'success',
    'notice',
    'error',
]

#: default type to use
DEFAULT_TYPE = 'info'


def add_flash(request, msg, type_=DEFAULT_TYPE):
    """Add a flash message
    
    """
    request.session.flash('%s %s' % (type_, msg))
