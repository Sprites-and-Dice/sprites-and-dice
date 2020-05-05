# models.py
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.functional import cached_property

from wagtail.images.image_operations import (
	DoNothingOperation, MinMaxOperation, WidthHeightOperation
)
from wagtail.images.models import (
	AbstractImage, AbstractRendition, Filter, Image
)

from wagtail.snippets.edit_handlers import SnippetChooserPanel


class CustomImage(AbstractImage):

	image_credit = models.CharField(max_length=250, blank=True)
	
	game = models.ForeignKey(
		'game.Game',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	admin_form_fields = Image.admin_form_fields + (
		'image_credit',
		'game'
	)

	def get_rendition(self, rendition_filter):
		"""Always return the source image file for GIF renditions."""
		if self.file.name.endswith('.gif'):
			return self.get_mock_rendition(rendition_filter)
		else:
			return super(CustomImage, self).get_rendition(rendition_filter)

	def get_mock_rendition(self, rendition_filter):
		"""
			Create a mock rendition object that wraps the original image.

			Using the template tag {% image image 'original' %} will return an
			<img> tag linking to the original file (instead of a file copy, as
			is default Wagtail behavior).

			Template tags with Wagtail size-related filters (width, height, max,
			and min), e.g. {% image image 'max-165x165' %}, will generate an
			<img> tag with appropriate size parameters, following logic from
			wagtail.images.image_operations.
		"""
		width  = self.width
		height = self.height

		for operation in rendition_filter.operations:
			if isinstance(operation, DoNothingOperation):
				continue

			if not any([
				isinstance(operation, WidthHeightOperation),
				isinstance(operation, MinMaxOperation),
			]):
				raise RuntimeError('non-size operations not supported on GIFs')

			width, height = self.apply_size_operation(operation, width, height)

		return CustomRendition(
			image  = self,
			file   = self.file,
			width  = width,
			height = height
		)

	@staticmethod
	def apply_size_operation(operation, width, height):
		class MockResizableImage(object):
			def __init__(self, width, height):
				self.width = width
				self.height = height

			def get_size(self):
				return self.width, self.height

			def resize(self, size):
				width, height = size
				self.width = width
				self.height = height

		mock_image = MockResizableImage(width, height)
		operation.run(mock_image, image=None, env={})
		return mock_image.width, mock_image.height

	# If the image is both large and its height-to-width ratio is approximately
	# 1/2 we instruct the template to render large Twitter cards
	# See https://dev.twitter.com/cards/types/summary-large-image
	@property
	def should_display_summary_large_image(self):
		image_ratio = float(self.height) / self.width
		return self.width >= 1000 and 0.4 <= image_ratio <= 0.6


class CustomRendition(AbstractRendition):
	image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

	class Meta:
		unique_together = (
			('image', 'filter_spec', 'focal_point_key'),
		)


# Delete the source image file when an image is deleted
@receiver(pre_delete, sender=CustomImage)
def image_delete(sender, instance, **kwargs):
	instance.file.delete(False)


# Delete the rendition image file when a rendition is deleted
@receiver(pre_delete, sender=CustomRendition)
def rendition_delete(sender, instance, **kwargs):
	instance.file.delete(False)
