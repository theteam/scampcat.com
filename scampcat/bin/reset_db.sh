ggg#!/bin/bash
# Please note that your virtual environment should be activated
export PIP_REQUIRE_VIRTUALENV=true
echo Make sure you have DEBUG=True in  your settings_local.py file
python manage.py reset_db --router=default
python manage.py syncdb
python manage.py loaddata fixtures/sites.json
#python manage.py loaddata fixtures/scamp.json
#python manage.py migrate scamp
