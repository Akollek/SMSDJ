# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=2, choices=[(b'RE', b'REQUESTED'), (b'DL', b'DOWNLOADED'), (b'PL', b'PLAYING'), (b'PD', b'PLAYED')])),
                ('request_text', models.CharField(max_length=300)),
                ('requested_by', models.CharField(max_length=10)),
                ('requested', models.DateTimeField(auto_now_add=True)),
                ('played', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('filepath', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='song',
            field=models.ForeignKey(to='dj.Song', null=True),
        ),
    ]
