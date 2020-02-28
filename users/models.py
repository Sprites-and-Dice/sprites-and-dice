from django.contrib.auth.models import AbstractUser
from django.db import models

from wagtail.core.fields import RichTextField

class User(AbstractUser):
	title = models.CharField(max_length=250, blank=True) 
	bio   = models.TextField(max_length=600, blank=True)
	# bio = RichTextField(blank=True) # Does not currently work - check in on https://github.com/wagtail/wagtail/issues/5961 for updates
