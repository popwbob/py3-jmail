# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('macct', '0004_auto_20141215_1916'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jmailmacct',
            options={'verbose_name': 'JMail Account', 'verbose_name_plural': 'JMail Accounts'},
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='password',
            field=models.CharField(default='', max_length=254),
            preserve_default=True,
        ),
    ]
