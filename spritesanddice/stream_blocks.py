from django import forms

from users.models import User

from wagtail.core import blocks
from wagtail.images.blocks    import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks  import SnippetChooserBlock

# Generic User Chooser
class UserChooserBlock(blocks.ChooserBlock):
	target_model = User
	widget       = forms.Select

	# Return the key value for the select field
	def value_for_form(self, value):
		if isinstance(value, self.target_model):
			return value.pk
		else:
			return value

	class Meta:
		icon = "user"


class PodcastBlock(blocks.StructBlock):
	podcast = SnippetChooserBlock('podcast.Podcast')

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context=parent_context)
		context['podcast'] = value['podcast']
		return context

	class Meta:
		template = 'podcast/player.html'


class ReviewBlock(blocks.StructBlock):
	game = SnippetChooserBlock('game.Game')

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context=parent_context)
		context['game'] = value['game']
		return context

	class Meta:
		template = 'blocks/review_block.html'


class AuthorBlock(blocks.StructBlock):
	user = UserChooserBlock()

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context=parent_context)
		context['user'] = value['user']
		return context

	class Meta:
		template = 'users/author_bio.html'


# Stream Blocks for all content types
stream_blocks = [
	# Default
	('image',     ImageChooserBlock()),
	('Rich_Text', blocks.RichTextBlock()),
]

# Basic Pages Only
basic_blocks = stream_blocks + [
	('Author_Bio',  AuthorBlock(icon='fa-user')),
]

# Blog Page Only
blog_blocks = stream_blocks + [
	('Podcast',     PodcastBlock(icon='fa-headphones')),
	('Review_Info', ReviewBlock(icon='fa-pencil')),
]
