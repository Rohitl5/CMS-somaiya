# Generated by Django 4.2.3 on 2023-10-07 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0017_alter_conference_about_conference_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewer',
            name='areaOfInterest',
        ),
    ]
