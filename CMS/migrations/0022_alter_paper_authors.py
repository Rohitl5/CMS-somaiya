# Generated by Django 4.2.3 on 2023-10-15 05:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0021_remove_paper_authors_paper_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='authors',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.author'),
        ),
    ]
