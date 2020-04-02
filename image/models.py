

# models.py
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.functional import cached_property
from django.dispatch import receiver

from wagtail.images.image_operations import (
    DoNothingOperation, MinMaxOperation, WidthHeightOperation
)
from wagtail.images.models import (
    AbstractImage, AbstractRendition, Filter, Image
)

class CustomImage(AbstractImage):
	# Add any extra fields to image here

	# eg. To add a caption field:
	# caption = models.CharField(max_length=255, blank=True)

	admin_form_fields = Image.admin_form_fields + (
		# Then add the field names here to make them appear in the form:
		# 'caption',
	)

	def get_rendition(self, rendition_filter):
		"""Always return the source image file for GIF renditions.

		CustomImage overrides the default Wagtail renditions behavior to
		always embed the original uploaded image file for GIFs, instead of
		generating new versions on the fly.
		"""
		if self.file.name.endswith('.gif'):
			return self.get_mock_rendition(rendition_filter)
		else:
			return super(CustomImage, self).get_rendition(rendition_filter)

	@cached_property
	def orientation(self):
		if self.is_portrait:
			return 'portrait'
		elif self.is_landscape:
			return 'landscape'
		elif self.is_square:
			return 'square'
		else:
			return None

	@cached_property
	def is_square(self):
		return self.height == self.width

	@cached_property
	def is_portrait(self):
		return self.height > self.width

	@cached_property
	def is_landscape(self):
		return self.height < self.width



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
