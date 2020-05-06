# Generated by Django 3.0.3 on 2020-05-06 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_auto_20200506_0600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='type',
            field=models.CharField(choices=[('video-game', 'Video Game'), ('tabletop-game', 'Tabletop'), ('book', 'Book'), ('movie', 'Movie')], default='video-game', max_length=30),
        ),
    ]
