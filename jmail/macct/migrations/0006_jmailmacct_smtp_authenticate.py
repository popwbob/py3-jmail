# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('macct', '0005_auto_20141217_0416'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmailmacct',
            name='smtp_authenticate',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
