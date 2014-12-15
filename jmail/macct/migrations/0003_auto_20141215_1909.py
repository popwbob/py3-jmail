# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('macct', '0002_jmailmacct_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmailmacct',
            name='imap_server',
            field=models.CharField(default='localhost', max_length=254),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='imap_server_port',
            field=models.PositiveSmallIntegerField(default=993),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='imap_server_ssl',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='smtp_server',
            field=models.CharField(default='localhost', max_length=254),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='smtp_server_port',
            field=models.PositiveSmallIntegerField(default=993),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jmailmacct',
            name='smtp_server_tls',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
