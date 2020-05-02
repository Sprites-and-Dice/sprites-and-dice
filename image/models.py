

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

	admin_form_fields = Image.admin_form_fields + ()

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
