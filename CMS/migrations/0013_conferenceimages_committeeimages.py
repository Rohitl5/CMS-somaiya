# Generated by Django 4.2.3 on 2023-09-28 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0012_remove_conference_committee_images_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='conferenceImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conference_images', models.FileField(null=True, upload_to='desktop')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.conference')),
            ],
        ),
        migrations.CreateModel(
            name='committeeImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committee_images', models.FileField(null=True, upload_to='desktop')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.conference')),
            ],
        ),
    ]
