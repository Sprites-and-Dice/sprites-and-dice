from podcast.models import Podcast

from wagtail.admin.site_summary import SummaryItem

PODCAST_ADMIN_LINK = '/admin/snippets/podcast/podcast/'

class PodcastSummaryItem(SummaryItem):
	template = 'wagtailadmin/home/site_summary_podcast.html'

	def get_context(self):
		count = Podcast.objects.all().count()
		return {
			'link': PODCAST_ADMIN_LINK,
			'count': count
		}
