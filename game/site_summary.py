from game.models import Game

from wagtail.admin.site_summary import SummaryItem

GAME_ADMIN_LINK = '/admin/game/game/'

class GameSummaryItem(SummaryItem):
	template = 'wagtailadmin/home/site_summary_game.html'

	def get_context(self):
		count = Game.objects.all().count()
		return {
			'link': GAME_ADMIN_LINK,
			'count': count
		}
