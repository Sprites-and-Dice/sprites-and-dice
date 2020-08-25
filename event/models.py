from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import InlinePanel, FieldPanel, StreamFieldPanel, MultiFieldPanel, HelpPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index
from wagtail.snippets.models import register_snippet

# ===== Snippet Models =====

@register_snippet
class Event(index.Indexed, ClusterableModel):

	title       = models.CharField(null=True, blank=True, max_length=255)
	description = models.TextField(null=True, blank=True)

	start_date = models.DateTimeField(null=True, blank=True)
	end_date   = models.DateTimeField(null=True, blank=True)

	type = models.CharField(max_length=30, choices=(
		('stream',     'Twitch Stream'),
		('online',     'Virtual Game Night'),
		('meatspace',  'In-Person Event'),
		('convention', 'Convention'),
		('other',      'Other'),
	), default='online')

	panels = [
		FieldPanel('title'),
		FieldPanel('description'),
		FieldPanel('type'),
		FieldPanel('start_date'),
		FieldPanel('end_date'),
	]

	def __str__(self):
		return self.title


# ===== ModelAdmin Models =====

class EventAdmin(ModelAdmin):
	model = Event
	list_display = ('title', 'type', 'start_date', 'end_date')
	search_fields = ['title', 'description']
	list_display_add_buttons = 'title'
	menu_icon = 'fa-calendar'

modeladmin_register(EventAdmin)
