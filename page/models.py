from bs4 import BeautifulSoup

from django.db import models
from django.utils.html import format_html
from django.http import HttpResponseRedirect

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from spritesanddice.stream_blocks import basic_blocks, blog_blocks

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

	def __str__(self):
		return self.tag.name


class BasePage(Page):

	show_in_sidebar = models.BooleanField(default=False)

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


# Generic Page - For things like /about, /contact, etc
class BasicPage(BasePage):
	parent_page_types = ['home.HomePage']

	content = StreamField(basic_blocks, blank=True)

	content_panels = BasePage.content_panels + [
		StreamFieldPanel('content'),
	]


# Folder for organizing Blog Posts
class BlogFolder(BasePage):
	parent_page_types = ['home.HomePage']

	icon = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	content_panels = BasePage.content_panels + [
		ImageChooserPanel('icon'),
		FieldPanel('show_in_menus'),
		FieldPanel('show_in_sidebar'),
	]

	promote_panels = BasePage.promote_panels + []


# Folder for making "Tag" menu items
class TagFolder(BlogFolder):
	parent_page_types = ['home.HomePage']
	subpage_types = []

	tag = models.ForeignKey(
		'taggit.Tag',
		null=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	content_panels = BlogFolder.content_panels + [
		FieldPanel('tag')
	]

	# Redirect to /tags/tag-slug
	def serve(self, request, *args, **kwargs):
		return HttpResponseRedirect('/tags/{}'.format(self.tag.slug), status=302)


class BlogPage(BasePage):
	parent_page_types = ['page.BlogFolder']

	header_image = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	header_video = models.URLField(max_length=250, blank=True)

	subtitle = models.CharField(max_length=250, blank=True)
	content  = StreamField(blog_blocks, blank=True)

	author   = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
	tags     = ClusterTaggableManager(through=PageTag, blank=True)

	legacy_id = models.IntegerField(null=True, blank=True) # Drupal 7 Node ID for imported legacy content

	enable_comments = models.BooleanField(default=False)

	def category(self):
		return self.get_parent()

	def disqus_identifier(self):
		# Drupal Disqus Identifiers were "node/123"
		if self.legacy_id:
			return "node/{}".format(self.legacy_id)
		else:
			return "page/{}".format(self.id)

	def header_title(self):
		return format_html(
			self.title.replace(':',':<br/>', 1).replace(' - ','<br/>', 1),
		)

	def sidebar_title(self):
		return format_html(
			'<br/>'.join(self.title.split('-')),
		)

	# Give editors the flexibility to change the public-facing post date
	# by using the "go_live_at" field - every query sorts by "-go_live_at"
	def post_date(self):
		if self.go_live_at:
			return self.go_live_at
		else:
			return self.first_published_at

	content_panels = BasePage.content_panels + [
		FieldPanel('subtitle'),
		MultiFieldPanel([
			ImageChooserPanel('header_image'),
			FieldPanel('header_video'),
		], heading="Header"),
		StreamFieldPanel('content'),
	]

	promote_panels = BasePage.promote_panels + [
		FieldPanel('tags'),
		FieldPanel('author'),
		FieldPanel('enable_comments'),
		MultiFieldPanel([
			InlinePanel('legacy_urls', label="URL Path")
		], heading="Legacy URLs")
	]

	search_fields = Page.search_fields + [
		index.SearchField('content', partial_match=True),
		index.RelatedFields('tags', [
			index.SearchField('name', partial_match=True)
		])
	]

	# def save(self):
		# if slug has changed:
		# 	# add a legacy URL
		#   # Send an API call to Disqus to tell them where the page can now be found
		# if the page is moving folders...
		#	figure out the full path of the old page, add as a legacy url

		# If "go_live_at" not set and the page is being published, set to last_published_at or current time

		# set disqus_identifier to "self.id"

class LegacyUrl(Orderable):
	blogpage = ParentalKey('BlogPage', related_name='legacy_urls', on_delete=models.CASCADE)

	path = models.CharField(max_length=255)

	panels = [ FieldPanel('path') ]

	# def clean(self):
		# validate that it is in slug format
		# validate that it does not conflict with existing URL paths on the site

	# def save():
		# if deleting, delete the associated redirect
		# if new, create an associated redirect
		# maybe add a 'redirect' field to the model that gets created on save() and deleted on_delete()
