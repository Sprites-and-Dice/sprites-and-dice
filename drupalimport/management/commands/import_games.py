from page.models import BlogPage, BlogFolder
from image.models import CustomImage
from game.models import Game
from podcast.models import Podcast

from bs4 import BeautifulSoup

from pprint import pprint

# =========== CONFIG =========

INPUT_JSON = 'drupalimport/data/games.json'

# ===== JSON =====

import json

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

# ===== Django Management Command =====

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	"""
	Import Games from JSON data
	"""
	def handle(self, *args, **options):
		json_data = open_json(INPUT_JSON)

		for g in json_data:
			pprint(g)
