from page.models import BlogPage, BlogFolder, PageTag
from bs4 import BeautifulSoup
from users.models import User
from taggit.models import Tag

from django.template.defaultfilters import slugify

from pprint import pprint

from wagtail.core.blocks.stream_block import StreamValue

# =========== CONFIG =========

BLOG_POSTS_FOLDER_ID = 738 # Local ID for "Migration Tests" folder
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

def convert_content_to_richtext_block(content):
	return [{
		'type': 'Rich_Text',
		'value': content,
	}]

# ===== Django Management Command =====

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	"""
	Import Blog Posts from JSON data
	"""
	def handle(self, *args, **options):
		json_data = open_json(INPUT_JSON)

		parent_page = BlogFolder.objects.get(id=BLOG_POSTS_FOLDER_ID)

		for n in json_data[:3]:

			# CREATE A NEW PAGE
			page = BlogPage(
				title   = n['title'],
				slug    = n['slug'],

				owner_id  = n['author_id'],
				author_id = n['author_id'],

				tags = ', '.join(n['tags']),

				first_published_at = convert_string_to_datetime(n['post_datetime']),
				last_published_at  = convert_string_to_datetime(n['revised_datetime']),
				latest_revision_created_at = convert_string_to_datetime(n['revised_datetime']),

				show_in_menus = False,
			)

			# Format blog post HTML as Stream Data for page.content
			stream_block = page.content.stream_block
			stream_data  = convert_content_to_richtext_block(n['content'])
			page.content = StreamValue(stream_block, stream_data, is_lazy=True)

			# Add this page as a child of the desired Blog Folder to create a DB instance
			parent_page.add_child(instance=page)
			print('Imported "{}"'.format(page.title))

			# Create Page Tags that point to this page
			for t in n['tags']:
				try:
					tag = Tag.objects.get(name=t)
				except:
					tag = Tag(name=t, slug=slugify(t))
				page_tag = PageTag(tag=tag, content_object=page)

				tag.save()
				page_tag.save()


			# Print import errors
			# "Slug already in use" will be raised on repeat attempts - this is ok
			# except Exception as e:
			# 	if "This slug is already in use" not in str(e):
			# 		print("============")
			# 		print("Failed to import {}".format(page.title))
			# 		pprint(e)
			# 		print("------------")

		print("Done!")
