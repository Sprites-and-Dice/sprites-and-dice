from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.images.edit_handlers import ImageChooserPanel

# Misc. site Settings go here

@register_setting
class HeaderSettings(BaseSetting):
	update_schedule = models.CharField(null=True, blank=True, max_length=255)

	panels = [
		FieldPanel('update_schedule'),
	]

@register_setting
class SidebarSettings(BaseSetting):
	pass

# SEO Settings
@register_setting
class MetaDataSettings(BaseSetting):

	image = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	panels = [
		ImageChooserPanel('image', help_text="The default image that will show in social media if another isn't available on the page."),
	]
