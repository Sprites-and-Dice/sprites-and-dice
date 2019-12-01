from wagtail.core import blocks
from wagtail.images.blocks    import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks  import SnippetChooserBlock

class PodcastBlock(blocks.StructBlock):
	podcast = SnippetChooserBlock('podcast.Podcast')

	class Meta:
		template = 'podcast/player.html'

class ReviewBlock(blocks.StructBlock):
	game = SnippetChooserBlock('game.Game')

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
