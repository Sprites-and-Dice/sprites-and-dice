from bs4 import BeautifulSoup

from datetime import datetime

from django.db import models
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from spritesanddice.stream_blocks import basic_blocks, blog_blocks

from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import FieldPanel, HelpPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.redirects.models import Redirect
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

	# Example XML date string: "Fri, 11 May 2018 10:12:46 -0400"
	def xml_lastbuilddate(self):
		if self.last_published_at:
			return datetime.strftime(self.last_published_at, "%a, %d %b %Y %H:%M:%S %z")

	# Example XML date string: "Fri, 11 May 2018 10:12:46 -0400"
	def xml_pubdate(self):
		if self.go_live_at:
			return datetime.strftime(self.go_live_at, "%a, %d %b %Y %H:%M:%S %z")

	def iso_last_modified(self):
		return datetime.isoformat(self.last_published_at)

	def iso_published(self):
		if self.go_live_at:
			return datetime.isoformat(self.go_live_at)

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
			HelpPanel(content="""
				<div style="max-width:650px;">
					<p>Use this section to maintain any known URL paths this page has had in the past.</p>
					<p>Once this page is published, the site will automatically create a <a href="/admin/redirects/" target="_blank">redirect</a> for you based on this list of legacy URLs if any changes you make cause this page's URL to change. This includes changing the "slug" field or moving the page to a new folder.</p>
					<p>Note: If you edit or delete one of these legacy URLs, the corresponding redirect will be updated / deleted as well.</p>
					<p>If this page has a comment thread, make sure to run the <a href="https://spritesanddice.disqus.com/admin/discussions/migrate/" target="_blank">Disqus Redirect Crawler</a> after verifying the redirect works so Disqus knows where this page has moved to.</p>
				</div>
			"""),
			InlinePanel('legacy_urls', label="URL Path")
		], heading="Legacy URLs")
	]

	search_fields = Page.search_fields + [
		index.SearchField('title', partial_match=True),
		index.SearchField('subtitle', partial_match=True),
		index.SearchField('content', partial_match=True),
		index.RelatedFields('tags', [
			index.SearchField('name', partial_match=True)
		]),
		index.RelatedFields('author', [
			index.SearchField('get_full_name', partial_match=True)
		])
	]

	def clean(self, *args, **kwargs):
		# Page feeds are sorted by "go_live_at".
		# Make sure go_live_at has a date set if the page is published
		if self.live and not self.go_live_at:
			self.go_live_at = self.last_published_at

		return super(BlogPage, self).clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		old = BlogPage.objects.filter(id=self.id).first() # Get the existing LegacyUrl in the DB
		if old:
			if old.url != self.url:
				legacy_url, created = LegacyUrl.objects.get_or_create(path=self.url, blogpage=self)
				legacy_url.save()
				if created:
					print("Created new LegacyUrl to reflect change in BlogPage URL.", legacy_url)
					# Send an API call to Disqus to tell them where the page can now be found

		return super(BlogPage, self).save(*args, **kwargs)



class LegacyUrl(Orderable):
	blogpage = ParentalKey('BlogPage', related_name='legacy_urls', on_delete=models.CASCADE)

	path = models.CharField(max_length=255)

	panels = [ FieldPanel('path') ]

	def clean(self, *args, **kwargs):
		# Normalise path to match how Wagtail will store it in a Redirect object
		self.path = Redirect.normalise_path(self.path)

		# Check that this redirect doesn't already exist for any other pages
		try: # Existing LegacyUrl
			existing_legacy_urls = LegacyUrl.objects.filter(path=self.path).exclude(blogpage=self.blogpage).count() > 0
			existing_redirects   = Redirect.objects.filter(old_path=self.path).exclude(redirect_page=self.blogpage).count() > 0
			if existing_legacy_urls or existing_redirects:
				raise ValidationError({'path': ["LegacyUrl conflicts with an existing legacy URL or redirect."]})
		except: # New LegacyUrl - Not associated with a page yet
			existing_legacy_urls = LegacyUrl.objects.filter(path=self.path).count() > 0
			existing_redirects   = Redirect.objects.filter(old_path=self.path).count() > 0
			if existing_legacy_urls or existing_redirects:
				raise ValidationError({'path': ["LegacyUrl conflicts with an existing legacy URL or redirect."]})

		return super(LegacyUrl, self).clean(*args, **kwargs)

	def delete(self, *args, **kwargs):
		"""
		if deleting, delete the associated redirect
		"""
		try:
			redirect = Redirect.objects.get(old_path=self.path, redirect_page=self.blogpage)
			print("Deleting redirect", redirect)
			redirect.delete()
		except:
			print("Failed to delete redirect for {}. It may have already been deleted.".format(self.path))

		return super(LegacyUrl, self).delete(*args, **kwargs)

	def save(self, *args, **kwargs):
		# Normalize path to match what will be in the DB
		self.path = Redirect.normalise_path(self.path)

		"""
		Check if path was updated - if so, update redirect
		"""
		old = LegacyUrl.objects.filter(id=self.id).first() # Get the existing LegacyUrl in the DB
		if old:
			if old.path != self.path: # Path has changed, find the old redirect and update
				try:
					old_redirect = Redirect.objects.get(old_path=old.path, redirect_page=self.blogpage)
					old_redirect.old_path = self.path
					old_redirect.save()
				except Exception as e:
					print("Failed to update Redirect associated with this LegacyUrl", self, e)

		"""
		Try to create a new Redirect if it does not already exist
		"""
		redirect, created = Redirect.objects.get_or_create(
			old_path=self.path,
			redirect_page=self.blogpage
		)
		if created:
			print("Created new redirect", redirect)

		return super(LegacyUrl, self).save(*args, **kwargs)
