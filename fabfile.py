# Fabric file for scampcat
import ConfigParser
import datetime
import os

from fabric.api import run, local, env, get, prompt, sudo, cd
from fabric.contrib import django
from fabric.contrib.console import confirm

django.settings_module('scampcat.settings.alfredo')
from django.conf import settings

here_dir = os.path.dirname(os.path.realpath(__file__))
here = lambda *x: os.path.join(here_dir, *x)

config = ConfigParser.ConfigParser()
config.readfp(open(here('fabric.cfg')))


env.project = config.get('general', 'project')
env.project_root = settings.PROJECT_ROOT
tmp_time = datetime.datetime.now()
env.time = tmp_time.strftime("%Y%m%d_%H%M")
env.media_root = settings.MEDIA_ROOT


def production():
    """Production server"""
    env.alias = 'production'
    env.hosts = config.get('production', 'hosts').split(',')
    env.user = config.get('production', 'user')
    env.path = config.get('production', 'path')
    env.db_name = config.get('production', 'db_name')
    env.db_user = config.get('production', 'db_user')
    env.db_pass = config.get('production', 'db_pass')
    env.branch = config.get('production', 'branch')
    env.release_name = '%(project)s_%(time)s' % env


def deploy(tag=None):
    """Deployment actions"""
    # override the version when one is created
    env.tag = tag if tag else ''
    if env.alias == 'production':
        if confirm("Are you sure you want to deploy to %(alias)s" % env):
            export_release()
            symlink_release()
            update_static()
    else:
        with cd(env.path):
            run('git pull origin %(version)s' % env)


def export_release():
    """Exports a release with the current time and date"""
    env.origin_path = "%s/src" % env.path
    run('cd %(origin_path)s && git pull --rebase %(tag)s' % env)
    run('cp -r %(origin_path)s %(path)s/releases/%(release_name)s' % env)


def symlink_release():
    """Removes the old release and symlinks latest release to current"""
    # remove current deployment
    run('rm %(path)s/current' % env)
    # symlink deployment
    run('ln -s %(path)s/releases/%(release_name)s/ %(path)s/current' % env)


def update_static():
    """Runs the new django collecstatic command"""
    if env.alias == 'production':
        with cd('%(path)s/current/scampcat/' % env):
            run('%(path)s/venv/bin/python manage.py collectstatic '
                '--settings=settings.production --noinput' % env)

def clean():
    """Remove pyc files from the server."""
    run('find %s -iname \*pyc -delete' % env.path)


def restart():
    """Copy the apache config for this site and restarts the server"""
    sudo('service apache2 restart', pty=False)


def dumpdb():
    """Dumps and retrieves the server database"""
    # dump of the database
    run("mysqldump -u%(db_user)s -p%(db_pass)s %(db_name)s > "
        "%(db_name)s-%(time)s.sql" % env)
    # compressing it
    run("tar cvfz %(db_name)s-%(time)s.sql.tgz %(db_name)s-%(time)s.sql" % env)
    # retrieve copy
    get("%(db_name)s-%(time)s.sql.tgz" % env,
        "%(db_name)s-%(time)s.sql.tgz" % env)
    # clean remote
    run("rm %(db_name)s-%(time)s.sql" % env)
    run("rm %(db_name)s-%(time)s.sql.tgz" % env)


def syncdb():
    """Syncs the database with the local one"""
    dumpdb()
    local("tar xvfz %(db_name)s-%(time)s.sql.tgz" % env)
    # get values from local_settings or prompt if empty
    settings.DATABASE_USER = settings.DATABASES['default']['USER']
    settings.DATABASE_PASSWORD = settings.DATABASES['default']['PASSWORD']
    settings.DATABASE_NAME = settings.DATABASES['default']['NAME']
    if settings.DATABASE_USER:
        env.local_db_user = settings.DATABASES['default']['USER']
    else:
        # prompt for details
        env.local_db_user = prompt("Database User:")
    if settings.DATABASE_PASSWORD or settings.DATABASE_PASSWORD == '':
        env.local_db_password = settings.DATABASE_PASSWORD
    else:
        env.local_db_password = prompt("Database password:")
    if settings.DATABASE_NAME:
        env.local_db_name = settings.DATABASE_NAME
    else:
        env.local_db_name = prompt("Database name:")
    env.local_connection = "mysql -u%(local_db_user)s -p%(local_db_password)s %(local_db_name)s" % env
    # drop existing database
    local("%(local_connection)s -e \"drop database %(local_db_name)s; "
          "create database %(local_db_name)s;\" " % env)
    # import database
    local("%(local_connection)s < %(db_name)s-%(time)s.sql" % env)
    # clean up
    local("rm %(db_name)s-%(time)s.sql.tgz" % env)
    local("rm %(db_name)s-%(time)s.sql" % env)
