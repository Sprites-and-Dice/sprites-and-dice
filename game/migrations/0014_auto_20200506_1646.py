# Generated by Django 3.0.3 on 2020-05-06 16:46

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_auto_20200506_0745'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewCopy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('code', models.CharField(blank=True, help_text='A download code, if it exists.', max_length=255, null=True)),
                ('notes', models.TextField(blank=True)),
                ('redeemed_by', models.CharField(blank=True, help_text='Who is reviewing this game?', max_length=255)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='game',
            name='format',
            field=models.CharField(blank=True, help_text='Card game, Miniatures game, Board game, etc.', max_length=255),
        ),
        migrations.AlterField(
            model_name='game',
            name='platforms',
            field=models.CharField(blank=True, help_text='PC, PS4, Virtual Boy, Vectrex, etc.', max_length=255),
        ),
        migrations.AlterField(
            model_name='game',
            name='play_time',
            field=models.CharField(blank=True, help_text='Average play session duration for board games, total playtime for some video games.', max_length=255),
        ),
        migrations.DeleteModel(
            name='ReviewCodes',
        ),
        migrations.AddField(
            model_name='reviewcopy',
            name='game',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_copies', to='game.Game'),
        ),
    ]
