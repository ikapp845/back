# Generated by Django 4.1.7 on 2023-07-13 16:17

from django.db import migrations
import django_ulid.models
import ulid.api.api


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0003_alter_askquestion_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='askquestion',
            name='id',
            field=django_ulid.models.ULIDField(default=ulid.api.api.Api.new, editable=False, primary_key=True, serialize=False),
        ),
    ]
