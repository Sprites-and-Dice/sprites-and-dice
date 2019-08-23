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
		'BlogPage',
		related_name='page_tags',
		on_delete=models.CASCADE,
	)

class BlogPage(Page):

	subtitle = models.CharField(max_length=250, blank=True)

	content = StreamField(sharedStreamFields, blank=True)

	tags = ClusterTaggableManager(through=PageTag, blank=True)

	content_panels = Page.content_panels + [
		FieldPanel('subtitle'),
		StreamFieldPanel('content'),
		FieldPanel('tags'),
	]

	promote_panels = Page.promote_panels + []

	search_fields = Page.search_fields + []
