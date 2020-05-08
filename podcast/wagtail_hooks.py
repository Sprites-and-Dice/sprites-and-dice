from podcast.site_summary import PodcastSummaryItem, PODCAST_ADMIN_LINK

from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

@hooks.register('construct_homepage_summary_items')
def add_podcast_summary_item(request, items):
	items.append(PodcastSummaryItem(request))

@hooks.register('register_admin_menu_item')
def register_color_menu_item():
	return MenuItem('Podcast', PODCAST_ADMIN_LINK, classnames='icon icon-fa-headphones', order=400)
