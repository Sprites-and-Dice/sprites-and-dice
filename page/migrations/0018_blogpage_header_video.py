# Generated by Django 3.0.3 on 2020-05-02 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0017_auto_20200502_0248'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='header_video',
            field=models.URLField(blank=True, max_length=250),
        ),
    ]
