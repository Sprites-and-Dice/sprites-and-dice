from django.contrib.auth.models import AbstractUser
from django.db import models

from wagtail.core.fields import RichTextField

class User(AbstractUser):
	bio = models.TextField(max_length=600, blank=True)
	# bio = RichTextField(blank=True) # Does not currently work - check in on https://github.com/wagtail/wagtail/issues/5961 for updates
