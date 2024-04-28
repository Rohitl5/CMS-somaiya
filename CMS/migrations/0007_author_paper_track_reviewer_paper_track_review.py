# Generated by Django 4.2.3 on 2023-09-20 11:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CMS', '0006_conference_organizingcommittee_advisorycommittee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conferences', models.ManyToManyField(to='CMS.conference')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('abstract', models.TextField()),
                ('file', models.FileField(upload_to='papers/')),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('under_review', 'Under Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='submitted', max_length=20)),
                ('keywords', models.TextField()),
                ('submissionDate', models.DateField()),
                ('authors', models.ManyToManyField(related_name='papers', to='CMS.author')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.conference')),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.conference')),
            ],
        ),
        migrations.CreateModel(
            name='Reviewer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('areaOfInterest', models.TextField()),
                ('papers', models.ManyToManyField(to='CMS.paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='paper',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.track'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relevance', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('writingStyle', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('reviewerConfidence', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('originality', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('result', models.CharField(choices=[('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20)),
                ('modeOfPreapartion', models.TextField()),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comments', models.TextField()),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.paper')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CMS.reviewer')),
            ],
            options={
                'unique_together': {('paper', 'reviewer')},
            },
        ),
    ]
