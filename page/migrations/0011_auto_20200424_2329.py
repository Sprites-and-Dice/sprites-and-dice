# Generated by Django 3.0.3 on 2020-04-24 23:29

from django.db import migrations
import spritesanddice.stream_blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0010_auto_20200424_0451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicpage',
            name='content',
            field=wagtail.core.fields.StreamField([('image', wagtail.images.blocks.ImageChooserBlock()), ('Rich_Text', wagtail.core.blocks.RichTextBlock()), ('Author_Bio', wagtail.core.blocks.StructBlock([('user', spritesanddice.stream_blocks.UserChooserBlock())], icon='fa-user')), ('User_Grid', wagtail.core.blocks.StructBlock([('users', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('user', spritesanddice.stream_blocks.UserChooserBlock())])))], icon='fa-users'))], blank=True),
        ),
    ]
