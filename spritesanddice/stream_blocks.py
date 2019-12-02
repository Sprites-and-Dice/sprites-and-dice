from wagtail.core import blocks
from wagtail.images.blocks    import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks  import SnippetChooserBlock

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

stream_blocks = [
	# Default
	('image', ImageChooserBlock()),
	('Rich_Text', blocks.RichTextBlock()),

	# Custom
	('Podcast', PodcastBlock(icon='fa-headphones')),
	('Review_Info', ReviewBlock(icon='fa-pencil')),
]
