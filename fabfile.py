import os
import platform

import django
from django.conf import settings
from fabric import Connection
from fabric import task
from django.test.utils import get_runner

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pubpubs.settings.production")


def pass_checks():
    if settings.DEBUG:
        user_input = input("Debug = True. Continue? Y/N:")
        if user_input.lower() != "y":
            return False
    if settings.ENV_FILE_PATH[-4:] != ".env_pubpub":
        print("Wrong .env! You have: " + settings.ENV_FILE_PATH)
        return False
    print("checks passed")
    return True


def pass_tests():
    return True
    print(
        "running tests...(not optimised using config.settings.test yet, unfortunately)"
    )
    django.setup()
    TestRunner = get_runner(settings=settings)
    test_labels = ()
    test_runner = TestRunner(
        noinput=True, parallel=True, settings="config.settings.test"
    )
    failures = test_runner.run_tests(test_labels)
    if failures:
        user_input = input("Some test failures! Continue? Y/N:")
        if user_input.lower() != "y":
            return True
        print("some test failures so stopping")
        return False
    return True


def web_update(ip_address, command, test=True):
    if not pass_checks():
        return

    if not command:
        if test:
            if not pass_tests():
                return
    """
    To deploy to production type: fab prod
    The connection has been hardcoded to ease the command
    """
    WINDOWS = platform.system() == "Windows"
    connect_kwargs = (
        {"key_filename": [os.environ["USERPROFILE"] + "/pubpub_private_key"]} if WINDOWS else {}
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

