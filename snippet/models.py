from django.db import models

from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

@register_snippet
class Game(index.Indexed, ClusterableModel):
	title = models.CharField(null=True, blank=True, max_length=255)

	panels = [
		FieldPanel('title'),
	]

	search_fields = [
		index.SearchField('title', partial_match=True),
	]

	def __str__(self):
		return self.title

# @register_snippet
# class ReviewCode(models.Model):
