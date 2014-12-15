# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        ('macct', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmailmacct',
            name='user',
            field=models.ForeignKey(to='user.JMailUser'),
            preserve_default=True,
        ),
    ]
