# Generated by Django 4.2.3 on 2023-09-29 02:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0014_rename_committee_images_committeeimages_committee_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='track',
            old_name='description',
            new_name='subDomains',
        ),
    ]
