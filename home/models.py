from django.db import models
from page.models import BlogPage
from wagtail.core.models import Page

class HomePage(Page):

	parent_page_types = []

	def get_context(self, request):
		context = super(HomePage, self).get_context(request)
		context['blog_posts'] = BlogPage.objects.live().order_by('-last_published_at')
		return context
