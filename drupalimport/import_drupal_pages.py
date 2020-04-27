from django.db import migrations, models

from page.models import BlogPage, PageTag
from podcast.models import Podcast
from game.models import Game
from image.models import CustomImage

BLOG_POSTS_FOLDER_ID = 15 # Local ID for "Migration Tests" folder

# ===== Format Data for various Stream Blocks ======

def map_content_block(data):
	return {
		'type': 'Rich_Text',
		'value': {
			'rich_text': data,
		},
	}

def map_podcast_block(data):
	return {
		'type':  'Podcast', # Podcast Snippet ID?
		'value': {
			'podcast': '',
		}
	}

def map_game_block(data):
	return {
		'type':  'Review_Info',
		'value': {
			'game': '', # Game snippet ID?
		}
	}

# Add HTML body content as StreamBlock data
# Also, create new CustomImage instances for every image referenced in the HTML
# If the image is external (and you can't programatically download them), create a list
def map_rich_text_block(node):
	# node_content = node['body']
	# stream_data  = []

	# stream_block = page.content.stream_block
	# page.content = StreamValue(stream_block, stream_data, is_lazy=True)
	# page.save()
	pass


# =============== Create Tags ===============

def create_blog_tags(node):
	# Create an array of tags from both the Categories and Tags field of the Drupal node
	# Drupal tags are formatted as a string separated by semicolon ";"
	tags = []
	tags += node.get('field_categories', '').split(';')
	tags += node.get('field_tags', '').split(';')

	# TODO: determine if Wagtail just accepts an array as input for tags
	return tags


# =============== Create Images ===============

def create_rich_text_images(rich_text_content):
	image_paths = []
	# TODO: Regex some image paths out of the page body
	pass

def create_header_image(node):
	# Example original image: "\/sites\/default\/files\/file-name.jpg"

	file_name = node['field_image'].replace('\/sites\/default\/files\/', '') # Strip old file path

	image = CustomImage(
		url = '/media/original_images/{}'.format(file_name)
	)
	image.save()

	return image


# =============== Create Snippets ===============

def create_game(node):
	game = Game(
		name              = node.get('field_game_name',''),
		author            = node.get('field_author',''),
		developer         = node.get('field_developer',''),
		publisher         = node.get('field_publisher',''),
		platforms         = node.get('field_platforms',''),
		other_info        = node.get('field_other_info',''), # NOTE - This may be multiple lines - will be split by a semicolon ";"
		release_date      = node.get('field_release_date',''),
		number_of_players = node.get('field_number_of_players',''),
		play_time         = node.get('field_playing_time',''),
		price             = node.get('field_msrp',''),
		format            = node.get('field_format',''),
	)
	game.save()
	return map_game_block(game)

def create_podcast(node):
	# Example Podcast Path: " public:\/\/podcast\/episodes\/Sprites and Dice Podcast Episode 8.mp3 (102.9 MB)",
	podcast_file = node['field_podcast_mp3'] # TODO: Convert from Drupal path to Django Media Path

	# Create a new Podcast snippet
	podcast = Podcast(
		file           = podcast_file,
		episode_number = int(node.get('field_episode_number',  '0')),
		description    = node.get('field_podcast_description', 'Missing Description'),
		title          = node.get('field_podcast_title',       'Missing Title'),
	)
	podcast.save()
	return map_podcast_block(podcast)


# =============== Migration Script ===============

def import_pages(nodes):
	blog_posts_folder = BlogPage.objects.get(id=BLOG_POSTS_FOLDER_ID)

	for n in nodes:
		# Get node content
		node = n['node']

		# SEO / URL INFO
		# node['Path'] # URL Path - do we set up a redirect to the new path here? Will have to decide before migrating

		# POST DATE
		# EXAMPLE TIMESTAMP: "04/14/2020 - 00:00" (These are in NEW YORK TIME)
		# node["created"]
		# node["changed"]
		# node["publish_on"]

		# Create a new BlogPage, populate with all data from the Drupal Node
		page = BlogPage(
			header_image = create_header_image(node),
			title        = node['title'],
			subtitle     = node.get('field_subtitle', ''),
			content      = map_rich_text_block(node),
			tags         = create_blog_tags(node),
			author_id    = map_author(node.get('uid', '')),
		)

		# If podcast data exists, create a new Podcast and add it to the end of the StreamBlock data
		show_podcast = node.get('field_show_podcast_player', False)
		if show_podcast == "Yes":
			podcast_block = create_podcast(node)

		# If game review data exists, create a new Game and add it to the beginning of the StreamBlock data
		has_review_info = "Any game fields are not null"
		if has_review_info:
			game_block = create_game(node)

		# Set the new BlogPost as a child of the "Blog Posts" folder
		blog_posts_folder.add_child(instance=page)

		# Create the first revision for this page and publish it
		page.save_revision().publish()

"""
✓ Body
✓ Title
✓ Subtitle
✓ Published? Y/N (N/A, the exported data will be filtered)

✓ AUTHOR ID
✓ "Authored On" / Post Date (This is three fields - will have to figure out what we want to carry over)

✓ Header Image (field_image)
✓ Video Embed (For youtube headers)

✓ URL Alias ("Path")

✓ Podcast Info:
	✓ Show Podcast Player: "Yes", "No", null
	✓ Podcast File
	✓ Episode Number
	✓ Episode Title
	✓ Episode Description

✓ Review Info:
	TEXT FIELDS
	✓ Game Name
	✓ Author
	✓ Developer
	✓ Publisher
	✓ Platforms
	✓ Format
	✓ Number of Players
	✓ Playing Time
	✓ MSRP
	✓ Release Date
	REPEATING FIELD
	✓ "Other Info"

# TAGS - will be combined
	✓ Categories (checkboxes)
	✓ Tags (text, freeform)

# ====== NEED MANUAL FOLLOW UP EDITS =====

- Header Caption (Don't bother migrating - used in exactly one place
	(HvZ Article, photo credit to Brandon for the header - manually copy this))
- URL Redirects (?) (N/A IN JSON EXPORTS - idk what do do about this really other than watch analytics like a hawk)
"""

#
# class Migration(migrations.Migration):
#
# 	dependencies = [
# 		('page', '0008_auto_20200416_2307'),
# 	]
#
# 	operations = [
# 		migrations.RunPython(import_pages, migrations.RunPython.noop),
# 	]


def import_only_page_names():
	pass
