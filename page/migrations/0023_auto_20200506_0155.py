# Generated by Django 3.0.3 on 2020-05-06 01:55

from django.db import migrations
import spritesanddice.stream_blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0022_blogpage_enable_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicpage',
            name='content',
            field=wagtail.core.fields.StreamField([('Image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False))])), ('Rich_Text', wagtail.core.blocks.RichTextBlock()), ('Author_Bio', wagtail.core.blocks.StructBlock([('user', spritesanddice.stream_blocks.UserChooserBlock())], icon='fa-user')), ('User_Grid', wagtail.core.blocks.StructBlock([('users', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('user', spritesanddice.stream_blocks.UserChooserBlock())])))], icon='fa-users'))], blank=True),
        ),
        migrations.AlterField(
            model_name='blogpage',
            name='content',
            field=wagtail.core.fields.StreamField([('Image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False))])), ('Rich_Text', wagtail.core.blocks.RichTextBlock()), ('Podcast', wagtail.core.blocks.StructBlock([('podcast', wagtail.snippets.blocks.SnippetChooserBlock('podcast.Podcast'))], icon='fa-headphones')), ('Game', wagtail.core.blocks.StructBlock([('game', wagtail.snippets.blocks.SnippetChooserBlock('game.Game'))], icon='fa-pencil'))], blank=True),
        ),
    ]
