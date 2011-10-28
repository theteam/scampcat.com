import site
import sys
import os

sys.stdout = sys.stderr

site.addsitedir('/opt/theteam/scampcat/venv/lib/python2.6/site-packages')
sys.path.insert(0, '/opt/theteam/scampcat/current')

os.environ['DJANGO_SETTINGS_MODULE'] = 'scampcat.settings.production'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
