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


class ImageBlock(blocks.StructBlock):
	image   = ImageChooserBlock()
	caption = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link'])

	class Meta:
		icon = "image"
		template = 'blocks/image_block.html'


class PodcastBlock(blocks.StructBlock):
	podcast = SnippetChooserBlock('podcast.Podcast')

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context=parent_context)
		context['podcast'] = value['podcast']
		return context

	class Meta:
		template = 'podcast/player.html'


class GameBlock(blocks.StructBlock):
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


class UserGrid(blocks.StructBlock):
	users = blocks.ListBlock(blocks.StructBlock([
		('user', UserChooserBlock()),
	]))

	def get_context(self, value, parent_context=None):
		context = super().get_context(value, parent_context=parent_context)
		context['users'] = [x['user'] for x in value['users']]
		return context

	class Meta:
		template = 'users/user_grid.html'


# Stream Blocks for all content types
stream_blocks = [
	# Default
	('Image',     ImageBlock()),
	('Rich_Text', blocks.RichTextBlock()),
]

# Basic Pages Only
basic_blocks = stream_blocks + [
	('Author_Bio', AuthorBlock(icon='fa-user')),
	('User_Grid',  UserGrid(icon='fa-users')),
]

# Blog Page Only
blog_blocks = stream_blocks + [
	('Podcast', PodcastBlock(icon='fa-headphones')),
	('Game',    GameBlock(icon='fa-pencil')),
]
