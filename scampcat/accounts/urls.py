from django.conf.urls.defaults import url, patterns


urlpatterns = patterns(
    'scampcat.accounts.views',
    url(r'^(?P<username>[-\w]+)/$', 'profile', 
        name="accounts_profile"),
)
