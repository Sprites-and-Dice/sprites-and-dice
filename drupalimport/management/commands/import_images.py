from page.models import BlogPage, BlogFolder
from image.models import CustomImage

from bs4 import BeautifulSoup

from pprint import pprint

# =========== CONFIG =========

BLOG_POSTS_FOLDER_ID = 15 # Local ID for "Migration Tests" folder
INPUT_JSON = 'drupalimport/data/images.json'

# ===== JSON =====

import json

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

# ===== Django Management Command =====

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	"""
	Import Images from JSON data
	"""
	def handle(self, *args, **options):
		json_data = open_json(INPUT_JSON)

		for i in json_data:
			pprint(i)
