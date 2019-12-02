from bs4 import BeautifulSoup

from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from spritesanddice.stream_blocks import stream_blocks

from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

class PageTag(TaggedItemBase):
	content_object = ParentalKey(
		'BlogPage',
		related_name='page_tags',
		on_delete=models.CASCADE,
	)


class BasePage(Page):
	content_panels = Page.content_panels + []
	promote_panels = Page.promote_panels + []
	search_fields  = Page.search_fields  + []

	# Returns the first 280 characters of rich text content
	def get_content_preview(self):
		preview_text = ""

		if(self.content):
			content = filter(lambda block: 'Rich_Text' in block.block_type, self.content)
			for block in content:
				# Strip all HTML tags
				soup = BeautifulSoup(block.value.source, 'html5lib')
				paragraphs = soup.find_all('p')

				for p in paragraphs:
					text = p.get_text(" ", strip=True)
					preview_text += text + " "

					if len(preview_text) > 280: 
						return preview_text

		return preview_text

	class Meta:
		abstract = True


class BlogPage(BasePage):
	header_image = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	subtitle = models.CharField(max_length=250, blank=True)
	content  = StreamField(stream_blocks, blank=True)
	tags     = ClusterTaggableManager(through=PageTag, blank=True)

	# TODO: Determine how disqus identifiers for old pages will be stored
	def disqus_identifier(self):
		return self.__str__()

	content_panels = BasePage.content_panels + [
		FieldPanel('subtitle'),
		ImageChooserPanel('header_image'),
		StreamFieldPanel('content'),
		FieldPanel('tags'),
	]

	promote_panels = BasePage.promote_panels + []

	search_fields  = BasePage.search_fields  + []
