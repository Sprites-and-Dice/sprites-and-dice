# Generated by Django 3.0.3 on 2020-05-02 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_game_designer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['title']},
        ),
        migrations.RenameField(
            model_name='game',
            old_name='name',
            new_name='title',
        ),
    ]
