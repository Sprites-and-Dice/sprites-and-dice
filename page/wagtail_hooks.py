from page.models import BlogPage, LegacyUrl

from wagtail.contrib.redirects.models import Redirect
from wagtail.core import hooks

# When a page moves, create a new LegacyUrl
@hooks.register('before_move_page')
def create_redirect_on_page_move(request, page, destination_page):
	if type(page) == BlogPage:
		old_url = Redirect.normalise_path(page.url)
		new_url = Redirect.normalise_path(destination_page.url + page.slug)

		# URLs are different, make a new LegacyUrl
		if old_url != new_url:
			legacy_url, created = LegacyUrl.objects.get_or_create(path=old_url, blogpage=page)
			legacy_url.save()

		# Check for existing LegacyUrls at the new path - if they exist, delete them
		existing_legacy_url = LegacyUrl.objects.filter(path=new_url).first()
		if existing_legacy_url:
			existing_legacy_url.delete()
