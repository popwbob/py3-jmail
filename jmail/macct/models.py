from django.db import models
from django.forms import ModelForm

from jmail.user.models import JMailUser


class JMailMAcct(models.Model):
    user = models.ForeignKey(JMailUser)
    address = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return '{}: {}'.format(str(self.user), str(self.address))


class JMailMAcctForm(ModelForm):
    class Meta:
        model = JMailMAcct
        fields = ['address']
