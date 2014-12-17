# 20141214: Racing campeón Argentino Tornedo 1ra División 2014!!!

from django.db import models
from django.contrib.auth.models import User


class JMailUser(models.Model):
    django_user = models.OneToOneField(User, primary_key=True)

    class Meta:
        verbose_name = 'JMail User'
        verbose_name_plural = 'JMail Users'

    def __str__(self):
        return str(self.django_user)
