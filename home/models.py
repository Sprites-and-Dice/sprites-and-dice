from django.db import models

from page.models import BlogPage

from spritesanddice.models import SiteSettings

from wagtail.core.models import Page


class HomePage(Page):

	parent_page_types = []

	def header_image(self):
		first_post = BlogPage.objects.live().public().order_by('-go_live_at').first()
		if first_post.header_image:
			return first_post.header_image
		else:
			return SiteSettings.objects.first().default_social_thumb

	def get_context(self, request):
		context = super(HomePage, self).get_context(request)
		context['blog_posts'] = BlogPage.objects.live().public().order_by('-go_live_at')
		return context
