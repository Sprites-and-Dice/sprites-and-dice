# Generated by Django 3.0.3 on 2020-05-02 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20200502_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='type',
            field=models.CharField(choices=[('video-game', 'Video Game'), ('tabletop-game', 'Tabletop Game'), ('book', 'Book')], default='video-game', max_length=30),
        ),
    ]
