# Generated by Django 5.1.4 on 2025-01-16 20:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_passwordresettoken_duplicated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_tokens', to=settings.AUTH_USER_MODEL),
        ),
    ]
