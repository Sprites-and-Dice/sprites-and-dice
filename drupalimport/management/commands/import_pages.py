from page.models import BlogPage, BlogFolder
from bs4 import BeautifulSoup
from users.models import User

# =========== CONFIG =========

BLOG_POSTS_FOLDER_ID = 15 # Local ID for "Migration Tests" folder
INPUT_JSON = 'drupalimport/data/pages.json'

# ===== JSON =====

import json

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

# ===== Functions =====

from datetime import datetime
# Example timestamp: Short Format: 04/26/2020 - 19:32
# In this case we manually add the time zone for New York / EST (UTC -05:00)
def convert_string_to_datetime(drupal_timestamp):
	return datetime.strptime(drupal_timestamp+" -0500", '%m/%d/%Y - %H:%M %z')

# ===== Django Management Command =====

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	"""
	Import Blog Posts from JSON data
	"""
	def handle(self, *args, **options):
		json_data = open_json(INPUT_JSON)

		parent_page = BlogFolder.objects.get(id=BLOG_POSTS_FOLDER_ID)

		for n in json_data:

			# CREATE A NEW PAGE
			page = BlogPage(
				title   = n['title'],
				slug    = n['slug'],
				# content = n['content'],

				owner_id  = n['author_id'],
				author_id = n['author_id'],

				first_published_at = convert_string_to_datetime(n['post_datetime']),
				last_published_at  = convert_string_to_datetime(n['revised_datetime']),
				latest_revision_created_at = convert_string_to_datetime(n['revised_datetime']),

				show_in_menus = False,
			)

			# Add this page as a child of the desired Blog Folder
			parent_page.add_child(instance=page)

			print('Imported "{}"'.format(page.title))
