from page.models import BlogPage
from image.models import CustomImage
from wagtailmedia.models import Media
from game.models import Game
from podcast.models import Podcast


def delete_everything():
	print("Deleting blog posts...")
	for x in BlogPage.objects.all():
		print(x.title)
		x.delete()
	print("Deleting images...")
	for x in CustomImage.objects.all():
		print(x.title)
		x.delete()
	print("Deleting Podcasts...")
	for x in Podcast.objects.all():
		print(x.title)
		x.delete()
	print("Deleting Games...")
	for x in Game.objects.all():
		print(x.title)
		x.delete()
	print("Deleting media files...")
	for x in Media.objects.all():
		print(x.title)
		x.delete()

# ======== Django Management Command =========

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = "Deletes everything in the environment, allowing for a clean initial import of data. Please for the love of god turn this off before deploying to prod."

	def handle(self, *args, **options):
		delete_everything()
