# Generated by Django 4.1.7 on 2023-03-08 09:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_profile_last_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_login',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 3, 8, 15, 21, 46, 686405), null=True),
        ),
    ]
