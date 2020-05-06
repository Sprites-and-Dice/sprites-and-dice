from bs4 import BeautifulSoup

from datetime import datetime

from django.db import IntegrityError
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from game.models import Game, OtherInfo

from image.models import CustomImage

from page.models import BlogPage, BlogFolder, PageTag, LegacyUrl

from podcast.models import Podcast

from pprint import pprint

from taggit.models import Tag

from users.models import User

from wagtail.core.blocks.stream_block import StreamValue
from wagtail.contrib.redirects.models import Redirect

from wagtailmedia.models import Media

import json, traceback, urllib

# =========== CONFIG =========

INPUT_JSON = 'drupalimport/data/pages.json'

BLOG_POSTS_FOLDER_ID = 16
PODCASTS_FOLDER_ID   = 9
REVIEWS_FOLDER_ID    = 4
NEWS_FOLDER_ID       = 7
PREVIEWS_FOLDER_ID   = 15

blog_folder     = BlogFolder.objects.get(id=BLOG_POSTS_FOLDER_ID)
review_folder   = BlogFolder.objects.get(id=REVIEWS_FOLDER_ID)
podcast_folder  = BlogFolder.objects.get(id=PODCASTS_FOLDER_ID)
news_folder     = BlogFolder.objects.get(id=NEWS_FOLDER_ID)
previews_folder = BlogFolder.objects.get(id=PREVIEWS_FOLDER_ID)

# ===== JSON =====

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

# ===== Data Transformation Functions =====

# Example timestamp: Short Format: 04/26/2020 - 19:32
# In this case we manually add the time zone for New York / EST (UTC -05:00)
def convert_string_to_datetime(drupal_timestamp):
	return datetime.strptime(drupal_timestamp+" -0500", '%m/%d/%Y - %H:%M %z')

def create_stream_block_podcast(podcast):
	return {
		'type':'Podcast',
		'value': {
			'podcast':podcast.id
		}
	}

def create_stream_block_game(game):
	return {
		'type':'Game',
		'value': {
			'game':game.id
		}
	}

def create_stream_block_image(data):
	image = create_image(data['src'], title=data['title'], alt=data['alt'])
	return {
		'type':  'Image',
		'value': {
			'image':   image.id if image else None,
			'caption': data['caption']
		}
	}

def convert_content_to_stream_blocks(content):
	stream_data = []
	for block in content:
		if block['type'] == 'rich_text':
			stream_data.append({
				'type':  'Rich_Text',
				'value': block['data'],
			})
		if block['type'] == 'image':
			image_block = create_stream_block_image(block['data'])
			if image_block:
				stream_data.append(image_block)
	return stream_data

# ===== Create new model instances / objects =====

def create_podcast(data):
	podcast = Podcast.objects.filter(title=data['title']).first()
	if not podcast:
		podcast = Podcast(
			title        = data['title'],
			description  = data['description'],
			publish_date = convert_string_to_datetime(data['publish_date']),
		)
		if data['episode_number']:
			podcast.episode_number = int(data['episode_number'])
			podcast.title = podcast.title.replace('#{}: '.format(podcast.episode_number), '')
		podcast.save()

		# Import MP3 File as a Media object
		file_name = data['podcast_file']
		file_path = 'drupalimport/podcasts/{}'.format(file_name)

		with open(file_path, "rb") as podcast_file:
			try:
				media_object, created = Media.objects.get_or_create(
					file = File(podcast_file, name=file_name),
					type = 'audio',
					duration = 0,
					defaults = { 'title': "Sprites and Dice Podcast: "+podcast.title }
				)
				media_object.save()
				print('PODCAST', media_object, created)
				if media_object and created:
					podcast.file = media_object
					podcast.save()
				else:
					podcast.delete()

			except Exception as e:
				print("Podcast Exception", e)

	return podcast

def create_game_other_info(text, game):
	other_info = OtherInfo(game=game, text=text)
	other_info.save()

def create_game(data):
	game = Game.objects.filter(title=data['title'].strip()).first()
	if not game:
		game = Game(title=data['title'].strip())

		# All optional fields
		if data['author']:
			game.author  = data['author'].strip()
		if data['developer']:
			game.developer = data['developer'].strip()
		if data['publisher']:
			game.publisher = data['publisher'].strip()
		if data['platforms']:
			game.platforms = data['platforms'].strip()
		if data['format']:
			game.format = data['format'].strip()
		if data['number_of_players']:
			game.number_of_players = data['number_of_players'].strip()
		if data['play_time']:
			game.play_time = data['play_time'].strip()
		if data['price']:
			game.price = data['price'].strip()

		game.save()

		# Fill out any additional "other info" lines
		other_info = data['other_info']
		if other_info:
			for text in other_info.split(';'): # Other info is semicolon-delimited list
				if text: # is truthy...
					create_game_other_info(text, game)

		# Release data isn't reliable to parse into a datetime object, make it an additional info item
		if data['release_date']:
			create_game_other_info(data['release_date'], game)

	return game

def create_image(file_name, alt="", title=""):
	if not title:
		title = file_name

	image = CustomImage.objects.filter(title=title).first()

	if image:
		return image
	else:
		path = 'drupalimport/images/{}'.format(file_name)
		try:
			with open(path, "rb") as image_file:
				try:
					image, created = CustomImage.objects.get_or_create(
						file     = ImageFile(image_file, name=title),
						defaults = { 'title': title }
					)
					if image and created:
						return image
				except IntegrityError:
					# image_file was not an image
					pass
		except FileNotFoundError:
			print("Could not create image - file does not exist.", file_name)
		except Exception as e:
			print("Image creation exception!!!", e)

	return None

def create_page_tags(page, tags):
	# Create Page Tags that point to this page
	for t in tags:
		slug = slugify(t)
		try:
			tag = Tag.objects.get(slug=slug) # Use name instead of slug since slugs are not case-sensitive
		except:
			print("Creating new tag", t)
			tag = Tag(name=t, slug=slugify(t))
			tag.save()
		page_tag = PageTag(tag=tag, content_object=page)
		page_tag.save()

def assign_page_to_parent_folder(page, tags):
	if 'Podcast' in tags:
		parent_page = podcast_folder
	elif 'Review' in tags:
		parent_page = review_folder
	elif 'Preview' in tags:
		parent_page = previews_folder
	elif 'News' in tags:
		parent_page = news_folder
	# Catch-all folder for all other posts
	else:
		parent_page = blog_folder

	parent_page.add_child(instance=page)

# ===== Django Management Command =====

class Command(BaseCommand):
	"""
	Import Blog Posts from JSON data
	"""
	def handle(self, *args, **options):
		json_data = open_json(INPUT_JSON)
		# json_data = json_data[:100] # Limit the number of imported pages while testing

		for n in json_data:
			publish_date = convert_string_to_datetime(n['post_datetime'])

			# Create a new page instance
			page = BlogPage(
				title    = n['title'],
				subtitle = urllib.parse.unquote(n['subtitle']),
				slug     = n['slug'],

				owner_id  = n['author_id'],
				author_id = n['author_id'],

				legacy_id = n['legacy_id'],

				first_published_at         = publish_date,
				last_published_at          = publish_date,
				latest_revision_created_at = publish_date,
				go_live_at                 = publish_date,

				show_in_menus = False,
			)

			if n['header_video']:
				page.header_video = n['header_video'].strip()

			# Import the Header Image
			header_image = create_image(n['header']['src'], title=n['header']['title'])
			if header_image:
				page.header_image = header_image

			# Format blog post HTML as Stream Data for page.content
			stream_block = page.content.stream_block
			stream_data  = convert_content_to_stream_blocks(n['content'])

			# Check for Game and Podcast data - Include them in the Stream Data if present

			# Create Podcast, if any
			podcast_data = n['podcast']
			if podcast_data:
				podcast = create_podcast(podcast_data)
				if podcast:
					podcast_block = create_stream_block_podcast(podcast)
					# Append a streamblock to the end of the page content
					stream_data = stream_data + [podcast_block]

			# Create Game, if any
			game_data = n['game']
			if game_data:
				game = create_game(game_data)
				if game:
					game_block = create_stream_block_game(game)
					# Prepend a streamblock to the beginning of the page content
					stream_data = [game_block] + stream_data

			# Save Stream Data to page.content
			page.content = StreamValue(stream_block, stream_data, is_lazy=True)

			try:
				# This page must exist in the Page tree somewhere to be saved
				# Add it as a child page of an existing folder.
				# Use tags to determine which parent it should have.
				assign_page_to_parent_folder(page, n['tags'])

				# Add legacy urls
				for url in n['legacy_urls']:
					legacy_url = LegacyUrl(path=url, blogpage=page)
					legacy_url.save()

				print('Imported "{}"'.format(page.title))

				# Now that the page exists, we can create PageTags that point to it.
				create_page_tags(page, n['tags'])

			# Print import errors
			except Exception as e:
				# if 'This slug is already in use' not in str(e):
				print("============")
				print("Failed to import {}".format(page.title))
				traceback.print_exc()
				print("------------")

		print("Done!")
