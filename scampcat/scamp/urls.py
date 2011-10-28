from django.conf.urls.defaults import url, patterns

from scampcat.scamp.views import (AnnotationDetailView, ScampDetailView, 
                                  ScampReorderView)

urlpatterns = patterns(
    'scampcat.scamp.views',
    url(r'^(?P<slug>[a-z0-9]+)/$', ScampDetailView.as_view(), 
        name="scamp_detail"),
    url(r'^(?P<slug>[a-z0-9]+)/reorder/$', ScampReorderView.as_view(), 
        name="scamp_reorder"),
    url(r'^(?P<slug>[a-z0-9]+)/tags/$', 'scamp_add_tags', 
        name="scamp_add_tags"),
    url(r'^(?P<slug>[a-z0-9]+)/claim/$', 'scamp_claim', 
        name="scamp_claim"),
    url(r'^(?P<slug>[a-z0-9]+)/clone/$', 'scamp_clone', 
        name="scamp_clone"),
    url(r'^(?P<slug>[a-z0-9]+)/toggle-lock/$', 'scamp_toggle_lock', 
        name="scamp_toggle_lock"),
    url(r'^(?P<slug>[a-z0-9]+)/tags/$', 'scamp_tags', 
        name="scamp_tags"),
    url(r'^(?P<slug>[a-z0-9]+)/flag/$', 'scamp_report', 
        name="scamp_report"),
    url(r'^(?P<slug>[a-z0-9]+)/delete/$', 'scamp_delete', 
        name="scamp_delete"),
    url(r'^(?P<scamp_slug>[a-z0-9]+)/(?P<annotation_id>[\d]+)/$',
        AnnotationDetailView.as_view(), name="annotation_detail"),
    url(r'^tags/(?P<tag>[-\w\s\.\+]+)/$', 'scamp_tags', 
        name="scamp_tags"),
    url(r'^$', 'homepage', name='homepage'),
)
