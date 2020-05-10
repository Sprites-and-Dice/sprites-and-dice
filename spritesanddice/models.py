from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.images.edit_handlers import ImageChooserPanel


@register_setting
class SiteSettings(BaseSetting):
	header_text = models.CharField(null=True, blank=True, max_length=255, help_text="Displayed below the site header in desktop mode.")
	slogan      = models.CharField(null=True, blank=True, max_length=255)

	default_social_thumb = models.ForeignKey(
		'image.CustomImage',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)

	panels = [
		FieldPanel('header_text'),
		FieldPanel('slogan'),
		MultiFieldPanel([
			HelpPanel(content="The default image that will show in social media if another isn't available on the page."),
			ImageChooserPanel('default_social_thumb'),
		], heading="Social Media Metadata")
	]
