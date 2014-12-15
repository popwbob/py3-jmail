# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('macct', '0003_auto_20141215_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jmailmacct',
            name='smtp_server_port',
            field=models.PositiveSmallIntegerField(default=25),
            preserve_default=True,
        ),
    ]
