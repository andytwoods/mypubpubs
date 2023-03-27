import getpass
import os

from fabric import Connection
from fabric import task
from invoke import Context

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pubpubs.settings.production")


@task
def prod(context):
    ip_address = '167.235.66.120'
    """
    To deploy to production type: fab prod
    """

    pword = getpass.getpass('Password: ')

    with Connection(
            host=ip_address, user="root", port=1337, connect_kwargs={'password': pword}
    ) as conn:
        conn.config.run.env = {"DJANGO_SETTINGS_MODULE": "pubpubs.settings.production"}
        with conn.cd("/root/pubpubs/mypubpubs"):
            with conn.prefix("source /root/venv/bin/activate"):
                conn.run("git pull")
                conn.run("pip install -r requirements/production.txt")
                conn.run("python manage.py migrate --settings=pubpubs.settings.production")
                # deploying vue components
                conn.run("python manage.py collectstatic --noinput --settings=pubpubs.settings.production")
                conn.run("sudo systemctl restart gunicorn")
                conn.run("sudo service nginx restart")
                conn.run("echo 'restarted gunicorn and nginx'")
                # conn.run("sudo supervisorctl restart huey")

        # it is done manually
        # with conn.cd('/home/ubuntu/production/git/my_staticfiles/vue/'):
        # conn.run('npm install')
        # conn.run('npm run build')


if __name__ == '__main__':
    context = Context()
    prod(context)
