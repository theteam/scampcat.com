from django.conf import settings
from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

# Custom error handlers.
handler404 = 'scampcat.common.views.not_found_handler'
handler500 = 'scampcat.common.views.error_handler'

urlpatterns = patterns(
    '',
    url(r'^admin/sentry/', include('sentry.web.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^registration/', include('social_auth.urls')),
    url(r'^liberate/', include('scampcat.liberation.urls')),
    url(r'^user/', include('scampcat.accounts.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^login/$', 'social_auth.views.auth', {'backend': 'twitter'},
        name='login'),
    url(r'^logout/$', 'scampcat.accounts.views.logout',
        name='logout'),
    url(r'^login/error/$', 'scampcat.accounts.views.login_error',
        name='login_error'),
    url(r'^404/$', 'scampcat.common.views.not_found_handler', name='404'),
    url(r'^500/$', 'scampcat.common.views.error_handler', name='500'),
)

urlpatterns += patterns(
    'django.views.generic.simple',
    url(r'^robots.txt$', 'direct_to_template', {'template': 'robots.txt',
                                                'mimetype': 'text/plain'}),
    url(r'^humans.txt$', 'direct_to_template', {'template': 'humans.txt',
                                                'mimetype': 'text/plain'}),
    url(r'^terms/$', 'direct_to_template', {'template': 'terms.html'},
        name='terms'),
    url(r'^privacy/$', 'direct_to_template', {'template': 'privacy.html'},
        name='privacy'),

)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

# Catch all and send to scamp urls.
urlpatterns += patterns(
    '',
    url(r'^', include('scampcat.scamp.urls')),
)
