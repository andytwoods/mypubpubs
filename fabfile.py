import os
import platform

import django
from django.conf import settings
from fabric import Connection
from fabric import task
from django.test.utils import get_runner

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pubpubs.settings.production")



def web_update(ip_address, command, test=True):

    """
    To deploy to production type: fab prod
    The connection has been hardcoded to ease the command
    """
    WINDOWS = platform.system() == "Windows"
    connect_kwargs = (
        {"key_filename": [os.environ["USERPROFILE"] + "/.ssh/pubpubs_rsa"]} if WINDOWS else {}
    )
    with Connection(
        ip_address, user="root", inline_ssh_env=True, connect_kwargs=connect_kwargs
    ) as conn:
        conn.config.run.env = {"DJANGO_SETTINGS_MODULE": "pubpubs.settings.production"}
        with conn.cd("/root/django-apps/mypubpubs/"):
            with conn.prefix("source ../VE/bin/activate"):
                if command:
                    conn.run(command)
                else:
                    conn.run("git pull")
                    conn.run("pip install -r requirements.txt")
                    conn.run("python manage.py migrate")
                    # deploying vue components
                    conn.run("python manage.py collectstatic --noinput")
                    conn.run("sudo supervisorctl restart sfpanel_production")
                    conn.run("sudo service nginx restart")
                    conn.run("sudo supervisorctl restart huey")

        # it is done manually
        # with conn.cd('/home/ubuntu/production/git/my_staticfiles/vue/'):
        # conn.run('npm install')
        # conn.run('npm run build')


def server_info(server: str):
    if server == "prod":
        return "18.168.214.24"
    elif server == "dev":
        return "18.168.219.187"
    elif server == "pwfl":
        return "3.9.132.132"
    elif server == "celery":
        return "18.130.218.97"


@task
def prod(_, command=None):
    web_update('109.237.27.137', command)

