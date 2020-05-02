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

from wagtailmedia.models import Media

import json, traceback

# =========== CONFIG =========

INPUT_JSON = 'drupalimport/data/pages.json'

BLOG_POSTS_FOLDER_ID = 1503
PODCASTS_FOLDER_ID   = 1504
REVIEWS_FOLDER_ID    = 1505
NEWS_FOLDER_ID       = 9

blog_folder    = BlogFolder.objects.get(id=BLOG_POSTS_FOLDER_ID)
review_folder  = BlogFolder.objects.get(id=REVIEWS_FOLDER_ID)
podcast_folder = BlogFolder.objects.get(id=PODCASTS_FOLDER_ID)
news_folder    = BlogFolder.objects.get(id=NEWS_FOLDER_ID)

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
	image = create_image(data['src'])
	if image:
		return {
			'type':  'Image',
			'value': {
				'image':   image.id,
				'caption': data['caption']
			}
		}
	else:
		return None

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
			podcast.title = podcast.title.replace('#{}: '.format('episode_number'), '')
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
	game = Game.objects.filter(name=data['name']).first()
	if not game:
		game = Game(name=data['name'])

		# All optional fields
		if data['author']:
			game.author  = data['author']
		if data['developer']:
			game.developer = data['developer']
		if data['publisher']:
			game.publisher = data['publisher']
		if data['platforms']:
			game.platforms = data['platforms']
		if data['format']:
			game.format = data['format']
		if data['number_of_players']:
			game.number_of_players = data['number_of_players']
		if data['play_time']:
			game.play_time = data['play_time']
		if data['price']:
			game.price = data['price']

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

def create_image(file_name):
	image = CustomImage.objects.filter(title=file_name).first()
	if image:
		return image
	else:
		path = 'drupalimport/images/{}'.format(file_name)
		try:
			with open(path, "rb") as image_file:
				try:
					image, created = CustomImage.objects.get_or_create(
						file     = ImageFile(image_file, name=file_name),
						defaults = { 'title': file_name }
					)
					if image and created:
						return image
				except IntegrityError:
					# image_file was not an image
					pass
		except FileNotFoundError:
			print("Could not create image - file does not exist.", file_name)
	return None

def create_page_tags(page, tags):
	# Create Page Tags that point to this page
	for t in tags:
		try:
			tag = Tag.objects.get(name=t)
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
			# Create a new page instance
			page = BlogPage(
				title    = n['title'],
				subtitle = n['subtitle'],
				slug     = n['slug'],

				owner_id  = n['author_id'],
				author_id = n['author_id'],

				first_published_at         = convert_string_to_datetime(n['post_datetime']),
				last_published_at          = convert_string_to_datetime(n['revised_datetime']),
				latest_revision_created_at = convert_string_to_datetime(n['revised_datetime']),

				show_in_menus = False,
			)

			# Import the Header Image
			header_image = create_image(n['header'])
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
				legacy_url = LegacyUrl(path=n['legacy_url'], blogpage=page)
				legacy_url.save()

				print('Imported "{}"'.format(page.title))

				# Now that the page exists, we can create PageTags that point to it.
				create_page_tags(page, n['tags'])

			# Print import errors
			except Exception as e:
				if 'This slug is already in use' not in str(e):
					print("============")
					print("Failed to import {}".format(page.title))
					traceback.print_exc()
					print("------------")

		print("Done!")
