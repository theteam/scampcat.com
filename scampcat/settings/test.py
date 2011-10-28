# test settings for scampcat
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ':memory:',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

app_list = []

for app in INSTALLED_APPS:
    if app != 'south':
        app_list.append(app)

INSTALLED_APPS = app_list + [
    'django_jenkins',
    ]

# Jenkins
PROJECT_APPS = [app for app in app_list if 'scampcat' in app]
JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                 'django_jenkins.tasks.with_coverage',
                 'django_jenkins.tasks.django_tests',
                 'django_jenkins.tasks.run_jslint',
                 'django_jenkins.tasks.run_pep8',
                 'django_jenkins.tasks.run_pyflakes',
)

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Nose settings
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
DEBUG = False

NOSE_ARGS = ['--with-xunit',
             '--with-coverage',
             '--cover-package=scampcat',
             '--cover-inclusive',
             '--cover-erase',
             '--nocapture',
             '--failure-detail',
             '--stop'
             #'--failed',
             #'--ipdb',
             ]
