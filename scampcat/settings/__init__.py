# Django settings for scampcat project.
import os
from django.contrib.messages import constants as message_constants
from S3 import CallingFormat

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
# settings is one directory up now
here = lambda *x: os.path.join(PROJECT_ROOT, '..', *x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = here('attachments')
MEDIA_URL = '/attachments/'
#MEDIA_URL = 'http://intranet.s3.amazonaws.com/'
STATIC_ROOT = here('static')
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of sttic files
STATICFILES_DIRS = (
    here('assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

FILE_UPLOAD_TEMP_DIR = '/tmp'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger'
}

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'scampcat.common.middleware.NyanCatMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# We store our sessions with our cache engine (memcached) for
# performance; we don't really have a need for prolonged persistence.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# As we're storing our sessions in cache, we use the session backend
# for messages also for better performance.
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'scampcat.urls'

TEMPLATE_DIRS = (
    here('templates'),
)

INSTALLED_APPS = (
    # Contrib Apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 3rd Party Apps
    'django_extensions',
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    'easy_thumbnails',
    'mediasync',
    'social_auth',
    'taggit',
    'pagination',
    #'south',
    # 1st Party Apps
    'scampcat.accounts',
    'scampcat.common',
    'scampcat.scamp',
    'scampcat.liberation',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


EMAIL_SUBJECT_PREFIX = '[scampcat] '
SEND_BROKEN_LINK_EMAILS = True

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
}

# AWS
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
THUMBNAIL_DEFAULT_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
AWS_S3_FILE_OVERWRITE = False
AWS_S3_SECURE_URLS = False


# media-sync
# This should match the version that we are deploying
MEDIA_AWS_PREFIX = 'v0'
MEDIASYNC = {
    'EXPIRATION_DAYS': 365 * 10,  # 10 years
    'SERVE_REMOTE': True,
    'DOCTYPE': 'html5',
    'BACKEND': 'mediasync.backends.s3',
    'AWS_BUCKET': "uk.co.theteam.clients.theteam.scampcat.assets",
    'MEDIA_ROOT': STATIC_ROOT,
    'AWS_PREFIX': MEDIA_AWS_PREFIX,
    'USE_SSL': False,
    'PROCESSORS': ('scampcat.common.backends.mediacompressor.css_minifier',
                   'scampcat.common.backends.mediacompressor.js_minifier'),
    'YUI_COMPRESSOR_PATH': here('bin', 'yuicompressor-2.4.5.jar'),
    'UGLIFY_COMPRESSOR_PATH': here('bin', 'uglify', 'bin', 'uglifyjs'),
    'JOINED': {
        'css/mainmin.css': ['css/base.css', ],
        'scripts/mainmin.js': [],
    },
}

# Django-markitup
MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})
MARKITUP_MEDIA_URL = STATIC_URL

# Twitter
AUTH_PROFILE_MODULE = 'accounts.UserProfile'

# oAuth twitter
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/login/error/'

# Pagination
PAGINATION_DEFAULT_PAGINATION = 5


# SCAMPCAT SETTINGS
if DEBUG:
    MEDIASYNC['SERVE_REMOTE'] = False
    MEDIASYNC['STATIC_URL'] = '/assets/'
