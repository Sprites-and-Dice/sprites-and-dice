from bs4 import BeautifulSoup
from pprint import pprint

# ============ Handle JSON Files =============

import json

# Paths for input/output
DRUPAL_JSON  = 'drupalimport/data/export-data.json'
PAGE_JSON    = 'drupalimport/data/pages.json'
IMAGE_JSON   = 'drupalimport/data/images.json'
GAME_JSON    = 'drupalimport/data/games.json'
PODCAST_JSON = 'drupalimport/data/podcasts.json'

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

def save_json(file_path, data):
	with open(file_path, 'w') as json_file:
		json.dump(data, json_file, indent=4)

# ========== Conversion Functions ===========

# TODO: Make these into author IDs that match wagtail author IDs - will need to pull down staging DB
def convert_author_id(drupal_author_id):
	authors = {
		4:   1, # "Jon Glover",
		133: 6, # "Shanna Wynn-Shirreffs",
		3:   2, # "Wyatt Krause",
		6:   4, # "Adam Factor",
		111: 7, # "Otto Kratky",
		9:   5, # "Eric Henn",

		# ID 3 is just "Test User"
		128: 3, # "Janene Andersen",
		99:  3, # "Peri Akman",
		102: 3, # "Alex Ellick",
		110: 3, # "Nate Brogan",
		122: 3, # "Brandon Doerrer",
		134: 3, # "Alton Campbell",
		92:  3, # "Milo Axelrod",
		91:  3, # "Reid Marshall",
		5:   3, # "Dana Kjolner",
		7:   3, # "Brandon Missig",
		8:   3, # "Miranda Waterman",
		10:  3, # "Ben Mayer",
		87:  3, # "Brian Isaia",
		143: 3, # "Jessica Fisher",
	}
	try:
		return authors[int(drupal_author_id)]
	except Exception as e:
		print("Error mapping author ID", e)

# Cut out the year/month, just get the slug
def convert_path_to_slug(drupal_path):
	slug = drupal_path.split('/')[-1]
	slug = slug.replace("%C3%A9", "e").replace("é","e") # Fix the "e" accent in "Pokemon"
	slug = slug.replace("%E2%80%99","") # Remove url-safe apostrophes
	slug = slug.replace("%E2%80%A6","") # Remove url-safe exclamation points
	slug = slug.replace("'", "").replace(":","").replace("!","").replace("#","") # Remove common symbols
	return slug

# Cut out the full path, just get the file name
def convert_image_to_filename(drupal_image_path):
	return drupal_image_path.split('/')[-1]

# Parse Drupal body HTML with BeautifulSoup
def parse_drupal_body(drupal_body):
	content  = drupal_body.replace("\n","") # Remove newline characters
	images   = []

	# Parse Body
	body = BeautifulSoup(drupal_body, "html5lib")

	# All images / captions were formatted as <table> elements.
	# Make sure images/captions don't get split up
	image_tables = body.find_all('table')
	for table in image_tables:
		table_images = table.find_all('img')
		if len(table_images) > 0:
			image   = table_images[0]
			caption = ''

			cells = table.find_all('td')
			for td in cells:
				if len(td.get_text(strip=True)) > 0:
					for c in td.contents:
						caption += str(c)
			image_data = {
				'src': image.get('src'),
				'alt': image.get('alt', ''),
				'caption': caption,
			}
			images.append(image_data)

	# TODO: Reformat page content and convert table/caption combos into rich text images w/ a "Caption" field

	return content, images

# ============ Create Assets =============

def create_image():
	pass

# ============ Main Script =============

wagtail_page_model = {}

def init():
	count = 0

	print("= = = = = = = = = = = = = = =")
	print("Loading JSON data...")

	drupal_data = open_json(DRUPAL_JSON)

	# Todo: Convert all data into fixures, one per model
	pages    = []
	podcasts = []
	games    = []
	images   = []

	# Loop through Drupal Data and add new Django pages one by one
	for node in drupal_data['nodes']:
		n = node['fields']

		page_id = int(n['Nid']) # Drupal's "Node ID". May be useful for re-attaching snippets to Pages after creation.

		# Parse the HTML body for images
		content, content_images = parse_drupal_body(n['body'])

		# Add images parsed from page content
		images += content_images

		# Build tags list from Tags/Categories fields
		tags = []
		node_tags = n.get('field_tags')
		node_categories = n.get('field_categories')
		if node_tags:
			tags += node_tags.split(';')
		if node_categories:
			tags += node_categories.split(';')

		# CREATE PAGE
		wagtail_page = {
			'title':     n['title'],
			'subtitle':  n.get('field_subtitle', ''),

			'content':   content, # Still just raw HTML - need to convert to StreamBlock data

			'author_id': convert_author_id(n['uid']),
			'slug':      convert_path_to_slug(n['path']),

			'tags': tags,

			'post_datetime':    n['created'],
			'revised_datetime': n['changed']
		}

		# CREATE HEADER IMAGE
		if n['field_image']:
			file_name = convert_image_to_filename(n['field_image'])
			image_data = {
				'file_name': file_name,
				'file_path': 'original_images/{}'.format(file_name),
			}
			images.append(image_data)

		# CREATE PODCAST
		if n['field_show_podcast_player'] and n['field_podcast_title']:
			podcasts.append({
				'title': n['field_podcast_title']
			})

		# CREATE GAME
		if n['field_game_name']:
			games.append({
				'name': n['field_game_name']
			})

		pages.append(wagtail_page)

	print("Saving...")

	print("Saved {} pages".format(len(pages)))
	save_json(PAGE_JSON,    pages)

	print("Saved {} podcasts".format(len(podcasts)))
	save_json(PODCAST_JSON, podcasts)

	print("Saved {} games".format(len(games)))
	save_json(GAME_JSON,    games)

	print("Saved {} images".format(len(images)))
	save_json(IMAGE_JSON,   images)

	print("Done!")

# ======== Django Management Command =========

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = "Convert exported Drupal JSON to Django Fixtures"

	def handle(self, *args, **options):
		init()
