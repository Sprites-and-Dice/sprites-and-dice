from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
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

class GameTag(TaggedItemBase):
	content_object = ParentalKey(
		'Game',
		related_name='game_tags',
		on_delete=models.CASCADE,
	)

@register_snippet
class Game(index.Indexed, ClusterableModel):

	box_art = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	title = models.CharField(max_length=255)

	type = models.CharField(max_length=30, choices=(
		('video-game',    'Video Game'),
		('tabletop-game', 'Tabletop Game'),
		('book',          'Book'),
	), default='video-game')

	author    = models.CharField(max_length=255, blank=True)
	designer  = models.CharField(max_length=255, blank=True)
	developer = models.CharField(max_length=255, blank=True)
	publisher = models.CharField(max_length=255, blank=True)

	platforms = models.CharField(max_length=255, blank=True)
	format    = models.CharField(max_length=255, blank=True)

	number_of_players = models.CharField(max_length=255, blank=True)
	play_time = models.CharField(max_length=255, blank=True)

	price        = models.CharField(max_length=255, blank=True)
	release_date = models.DateField(blank=True, null=True)

	tags = ClusterTaggableManager(through=GameTag, blank=True)

	panels = [
		FieldPanel('title', classname='full title'),

		FieldPanel('type'),

		ImageChooserPanel('box_art'),

		FieldPanel('author', help_text="For books"),
		FieldPanel('designer'),
		FieldPanel('developer'),
		FieldPanel('publisher'),

		FieldPanel('platforms', help_text='PC, PS4, Virtual Boy, Vectrex, etc.'),
		FieldPanel('format', help_text="Card game, Miniatures game, Board game, etc."),
		FieldPanel('number_of_players'),
		FieldPanel('play_time', help_text="Average play session duration for board games, total playtime for some video games."),
		FieldPanel('price'),
		FieldPanel('release_date'),
		InlinePanel('other_info', heading="Other Info"),

		InlinePanel('review_codes', heading="Review codes"),

		FieldPanel('tags'),
	]

	def available_codes(self):
		return self.review_codes.filter(redeemed=False).count()

	def review_codes_(self):
		return self.review_codes.count()

	def thumbnail(self):
		if self.box_art:
			return format_html(
					'<img class="box-art" style="margin:auto; display:block; max-height:175px;" src="{}" />',
					self.box_art.get_rendition('height-100').file.url
				)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ["title"]

# ===== Orderables =====

class OtherInfo(Orderable):
	game = ParentalKey('Game', related_name='other_info', on_delete=models.CASCADE)

	label = models.CharField(max_length=255, blank=True)
	text  = models.CharField(max_length=255)

	panels = [
		FieldPanel('label', help_text='Optional'),
		FieldPanel('text'),
	]

class ReviewCodes(Orderable):
	game = ParentalKey('Game', related_name='review_codes', on_delete=models.CASCADE)

	code = models.CharField(max_length=255, null=True, blank=True)
	notes = models.TextField(blank=True)
	redeemed = models.BooleanField(default=False)
	redeemed_by = models.CharField(max_length=255, blank=True)

	panels = [
		FieldPanel('code'),
		FieldPanel('notes'),
		FieldPanel('redeemed'),
		FieldPanel('redeemed_by'),
	]

# ===== ModelAdmin Models =====

class GameAdmin(ModelAdmin):
	model = Game
	list_display = ('thumbnail', 'title', 'developer', 'publisher', 'review_codes_')
	search_fields = [
		'title',
		'author',
		'designer',
		'developer',
		'publisher',
		'platforms',
		'format',
		'number_of_players',
		'play_time',
		'price',
	]
	list_display_add_buttons = 'title'
	menu_icon  = 'fa-gamepad'

modeladmin_register(GameAdmin)
