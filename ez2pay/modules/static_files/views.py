from __future__ import unicode_literals

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.path import AssetResolver


@view_config(route_name='static_files.favicon')
def favicon_view(request):
    resolver = AssetResolver()
    path = resolver.resolve('ez2pay:static/favicon.ico').abspath()
    file_ = open(path, 'rb')
    return Response(app_iter=file_, content_type=b'image/x-icon')
