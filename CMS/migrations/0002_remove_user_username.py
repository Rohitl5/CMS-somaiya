# Generated by Django 4.2.3 on 2023-09-17 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]