# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jmailuser',
            options={'verbose_name': 'JMail User', 'verbose_name_plural': 'JMail Users'},
        ),
    ]
