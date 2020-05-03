from django.contrib.auth.models import AbstractUser
from django.db import models

from wagtail.core.fields import RichTextField

class User(AbstractUser):
	title = models.CharField(max_length=250, blank=True)
	bio   = models.TextField(max_length=600, blank=True)
	# bio = RichTextField(blank=True) # Does not currently work - check in on https://github.com/wagtail/wagtail/issues/5961 for updates

	# Social Media Info
	show_email = models.BooleanField(default=False)
	twitter    = models.CharField(max_length=250, blank=True)
	website    = models.URLField(max_length=250, blank=True)

	# Make it easier to read usernames in chooser forms
	def __str__(self):
		return self.get_full_name()

	# IE "gif", "png"
	def avatar_file_type(self):
		if self.wagtail_userprofile.avatar:
			return self.wagtail_userprofile.avatar.file.name[-3:]
		return None
