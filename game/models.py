from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

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
class Game(index.Indexed, ClusterableModel):

	name = models.CharField(max_length=255)

	author    = models.CharField(max_length=255, blank=True)
	developer = models.CharField(max_length=255, blank=True)
	publisher = models.CharField(max_length=255, blank=True)

	platforms = models.CharField(max_length=255, blank=True)
	format    = models.CharField(max_length=255, blank=True)

	number_of_players = models.CharField(max_length=255, blank=True)
	play_time = models.CharField(max_length=255, blank=True)

	price        = models.CharField(max_length=255, blank=True)
	release_date = models.DateTimeField(blank=True, null=True)

	panels = [
		FieldPanel('name', classname='full title'),

		FieldPanel('author', help_text="For books"),
		FieldPanel('developer'),
		FieldPanel('publisher'),

		FieldPanel('platforms', help_text='PC, PS4, Virtual Boy, Vectrex, etc.'),
		FieldPanel('format', help_text="Card game, Miniatures game, Board game, etc."),
		FieldPanel('number_of_players'),
		FieldPanel('play_time', help_text="Average play session duration for board games, total playtime for some video games."),
		FieldPanel('price'),
		FieldPanel('release_date'),
		InlinePanel('other_info', heading="Other Info"),
	]

	def __str__(self):
		return self.name

	class Meta:
		ordering = ["name"]

# ===== Orderables =====

class OtherInfo(Orderable):
	game = ParentalKey('Game', related_name='other_info', on_delete=models.CASCADE)

	label = models.CharField(max_length=255, blank=True)
	text  = models.CharField(max_length=255)

	panels = [
		FieldPanel('label', help_text='Optional'),
		FieldPanel('text'),
	]


# ===== ModelAdmin Models =====

class GameAdmin(ModelAdmin):
	model = Game
	list_display = ('name',)
	search_fields = ['name']
	list_display_add_buttons = 'name'
	menu_icon  = 'fa-gamepad'

modeladmin_register(GameAdmin)
