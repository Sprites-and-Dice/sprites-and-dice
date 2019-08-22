from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

sharedStreamFields = [
    ('heading', blocks.CharBlock(classname="full title")),
    ('paragraph', blocks.RichTextBlock()),
    ('image', ImageChooserBlock()),
]

class PageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BasePage',
        related_name='page_tags',
        on_delete=models.CASCADE,
    )

# Model for all other page types to be based off of
class BasePage(Page):
    subtitle = models.CharField(max_length=250, blank=True)

    body = StreamField(sharedStreamFields, blank=True)
    tags = ClusterTaggableManager(through=PageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        StreamFieldPanel('body'),
        FieldPanel('tags'),
    ]

    promote_panels = Page.promote_panels + []

    search_fields = Page.search_fields + []

# class PodcastPage(BasePage):
    # audio_file          =
    # episode_number      =
    # episode_title       =
    # episode_description =

    # content_panels = BasePage.content_panels + []
