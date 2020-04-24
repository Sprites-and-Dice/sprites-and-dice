from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting

# Misc. site Settings go here

@register_setting
class HeaderSettings(BaseSetting):
	update_schedule = models.CharField(null=True, blank=True, max_length=255)

	panels = [
		FieldPanel('update_schedule'),
	]
