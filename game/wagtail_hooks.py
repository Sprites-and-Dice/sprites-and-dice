from game.site_summary import GameSummaryItem, GAME_ADMIN_LINK

from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

@hooks.register('construct_homepage_summary_items')
def add_game_summary_item(request, items):
	items.append(GameSummaryItem(request))
