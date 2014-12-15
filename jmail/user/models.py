# 20141214: Racing campeón Argentino Tornedo 1ra División 2014!!!

from django.db import models
from django.contrib.auth.models import User


class JMailUser(models.Model):
    django_user = models.OneToOneField(User)
