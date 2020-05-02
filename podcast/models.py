from datetime import datetime, timedelta

from django.db import models
from django.http import HttpResponseRedirect

from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.documents.models import Document
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from wagtailmedia.edit_handlers import MediaChooserPanel

@register_setting
class PodcastSettings(BaseSetting):
	title       = models.CharField(null=True, blank=True, max_length=255)
	description = models.TextField(null=True, blank=True)

	panels = [
		MultiFieldPanel([
			FieldPanel('title'),
			FieldPanel('description'),
		], heading="Podcast Feed Settings")
	]

	def save(self, *args, **kwargs):
		# TODO: IF CHANGES AFFECT PODCAST METADATA, UPDATE ALL EPISODES
		# episodes = Podcast.objects.all()
		# for e in episodes:
		#	# update here
		#	e.save()
		super(PodcastSettings, self).save(*args, **kwargs)

@register_snippet
class Podcast(index.Indexed, ClusterableModel):

	file = models.ForeignKey(
		'wagtailmedia.Media',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='podcast_file'
	)

	episode_number = models.IntegerField(null=True, blank=True)
	title          = models.CharField(null=True, blank=True, max_length=255)
	description    = models.TextField(null=True, blank=True)
	publish_date   = models.DateTimeField(null=True, blank=True)

	panels = [
		MediaChooserPanel('file'),
		FieldPanel('episode_number'),
		FieldPanel('title'),
		FieldPanel('description'),
		FieldPanel('publish_date'),
	]

	search_fields = [
		index.SearchField('title', partial_match=True),
		index.SearchField('description', partial_match=True),
	]

	def __str__(self):
		return self.title

	def episode_length(self):
		if(self.file):
			return timedelta(seconds=self.file.duration)
		else:
			return timedelta(seconds=0)

	def save(self, *args, **kwargs):
		# EDIT MP3 METADATA/FILENAME HERE
		# https://eyed3.readthedocs.io/en/latest/
		super(Podcast, self).save(*args, **kwargs)
