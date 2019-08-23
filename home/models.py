from django.db import models
from page.models import BlogPage
from wagtail.core.models import Page

class HomePage(Page):
	def get_context(self, request):
		context = super(HomePage, self).get_context(request)
		context['blog_posts'] = BlogPage.objects.live().public()
		return context
