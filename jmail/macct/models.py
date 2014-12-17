from django.db import models
from django.forms import ModelForm

from jmail.user.models import JMailUser


class JMailMAcct(models.Model):
    user = models.ForeignKey(JMailUser)
    address = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254, default='')
    imap_server = models.CharField(max_length=254, default='localhost')
    imap_server_port = models.PositiveSmallIntegerField(default=993)
    imap_server_ssl = models.BooleanField(default=True)
    smtp_server = models.CharField(max_length=254, default='localhost')
    smtp_server_port = models.PositiveSmallIntegerField(default=25)
    smtp_server_tls = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'JMail Account'
        verbose_name_plural = 'JMail Accounts'

    def __str__(self):
        return '{}: [{}] {}'.format(str(self.user), str(self.id), str(self.address))


class JMailMAcctForm(ModelForm):
    class Meta:
        model = JMailMAcct
        fields = [
            'address',
            'password',
            'imap_server',
            'imap_server_port',
            'imap_server_ssl',
            'smtp_server',
            'smtp_server_port',
            'smtp_server_tls',
        ]
