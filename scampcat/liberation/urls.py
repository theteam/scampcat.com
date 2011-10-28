from django.conf.urls.defaults import url, patterns

from piston.resource import Resource
from scampcat.liberation.handlers import LiberationHandler

liberation_resource = Resource(handler=LiberationHandler)

urlpatterns = patterns(
    'scampcat.liberation.views',
    url(r'^export.(?P<emitter_format>.+)$', liberation_resource,
        name='liberate_format'),
)
