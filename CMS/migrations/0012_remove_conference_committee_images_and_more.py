# Generated by Django 4.2.3 on 2023-09-28 02:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0011_conference_programchair'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conference',
            name='committee_images',
        ),
        migrations.RemoveField(
            model_name='conference',
            name='conference_images',
        ),
    ]
