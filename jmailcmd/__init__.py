def main():

    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmail.settings")
    from django.conf import settings

    settings.DEBUG = False
    settings.ALLOWED_HOSTS.append("localhost")

    from django.core.management import execute_from_command_line
    execute_from_command_line(["jmail", "runserver",
            "--insecure", "--noreload", "localhost:6080"])
