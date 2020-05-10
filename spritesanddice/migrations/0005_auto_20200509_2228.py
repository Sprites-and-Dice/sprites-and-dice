# Generated by Django 3.0.3 on 2020-05-09 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0045_assign_unlock_grouppagepermission'),
        ('image', '0003_customimage_game'),
        ('spritesanddice', '0004_delete_sidebarsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header_text', models.CharField(blank=True, help_text='Displayed below the site header in desktop mode.', max_length=255, null=True)),
                ('slogan', models.CharField(blank=True, max_length=255, null=True)),
                ('default_social_thumb', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='image.CustomImage')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='metadatasettings',
            name='image',
        ),
        migrations.RemoveField(
            model_name='metadatasettings',
            name='site',
        ),
        migrations.DeleteModel(
            name='HeaderSettings',
        ),
        migrations.DeleteModel(
            name='MetaDataSettings',
        ),
    ]