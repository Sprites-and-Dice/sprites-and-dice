from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from users.views import change_bio

from wagtail.core import hooks

@hooks.register('register_admin_urls')
def register_admin_urls():
	return [
		url(r'^account/bio/$', change_bio, name='wagtailadmin_custom_account_change_bio'),
	]

@hooks.register('register_account_menu_item')
def register_account_change_bio(request):
	return {
		'url': reverse('wagtailadmin_custom_account_change_bio'),
		'label': _('Change bio'),
		'help_text': _('Update your author bio.'),
	}
