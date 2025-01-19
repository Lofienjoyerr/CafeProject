# Generated by Django 5.1.4 on 2025-01-15 00:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_email_emailaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerifyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('email_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='users.emailaddress')),
            ],
        ),
    ]
