# Generated by Django 4.1.7 on 2023-03-08 10:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0011_alter_groupquestion_time'),
        ('user', '0011_alter_profile_last_login'),
        ('likes', '0010_alter_like_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 3, 8, 15, 33, 48, 754727), null=True),
        ),
        migrations.CreateModel(
            name='AskedLike',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(blank=True, default=datetime.datetime(2023, 3, 8, 15, 33, 48, 754727), null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.group')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.askquestion')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fromuserask', to='user.profile')),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='touserask', to='user.profile')),
            ],
        ),
    ]
