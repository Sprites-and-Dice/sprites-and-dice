import os
from django.conf import settings

def global_vars(request):
	return {
		'VERSION': settings.SPRITES_VERSION
	}
