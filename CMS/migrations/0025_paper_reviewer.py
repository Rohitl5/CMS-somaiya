# Generated by Django 4.2.3 on 2023-10-18 00:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0024_alter_reviewer_conference'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='reviewer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='CMS.reviewer'),
        ),
    ]