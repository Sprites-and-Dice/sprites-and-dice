# Generated by Django 3.0.3 on 2020-04-25 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20191202_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='designer',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
