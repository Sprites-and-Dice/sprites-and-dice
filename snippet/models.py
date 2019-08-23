from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet

@register_snippet
class Game(models.Model):
	title = models.CharField(null=True, blank=True, max_length=255)

	panels = [
		FieldPanel('title'),
	]

	def __str__(self):
		return self.title

# @register_snippet
# class ReviewCode(models.Model):
