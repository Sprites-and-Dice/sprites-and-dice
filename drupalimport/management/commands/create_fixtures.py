from bs4 import BeautifulSoup
from pprint import pprint
from django.utils.html import format_html

import urllib, os

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

def content_block(data):
	return {
		'type': 'rich_text',
		'data': data
	}

def parse_youtube_link(url):
	return url.replace("?feature=player_embedded","")

# Parse Drupal body HTML with BeautifulSoup
def parse_drupal_body(drupal_body):
	raw_html = drupal_body.replace("\n","").replace("&lt;","<").replace("&gt;",">").replace("&#x27;","'").replace("<!--more-->","")
	content  = []

	# Parse Body
	html = BeautifulSoup(raw_html, "html5lib")
	body = html.body

	# Strip all unneeded attributes
	for tag in html():
		unwanted_attributes = [
			"align",
			"mozallowfullscreen", "webkitallowfullscreen",
			"style", "stlye", "dir", "border", "cellpadding", "cellspacing",
			"allow", "typeof", "allowfullscreen", "frameborder"
		]
		for attribute in unwanted_attributes:
			del tag[attribute]

	# Replace Blogger embed videos with <embed> tags
	for tag in html.find_all("object", class_="BLOGGER-youtube-video"):
		# Find the inner embed tag
		if tag.find('embed'):
			new_tag = html.new_tag("embed")
			new_tag.attrs['src']  = parse_youtube_link(tag.find('embed').attrs['src'])
			new_tag.attrs['embedtype'] = 'video' # Wagtail "Media" rich text feature?
			tag.replace_with(new_tag)

	# Replace Youtube iFrames with <embed> tags
	for tag in html.find_all("iframe"):
		print("IFRAME", tag)
		new_tag = html.new_tag("embed")
		new_tag.attrs['src']  = parse_youtube_link(tag.attrs['src'])
		new_tag.attrs['embedtype'] = 'video' # Wagtail "Media" rich text feature?
		tag.replace_with(new_tag)

	# Do somethin' with twitter embeds
	for tag in html.find_all("blockquote", class_="twitter-tweet"):
		print("TWEET", tag)

	# Swap div.pull-quote for <blockquote>
	for tag in html.find_all("div", class_="pull-quote"):
		new_tag = html.new_tag("blockquote")
		new_tag.string = tag.string
		tag.replace_with(new_tag)

	# Remove invisible elements
	for tag in html.find_all("h2", class_="element-invisible"):
		tag.decompose()
	for tag in html.find_all("a", id_="more"):
		tag.decompose()

	# Strip empty <p>'s and <div>'s
	for tag in html.find_all('p') + html.find_all('div'):
		if tag.string and tag.string.strip() == '':
			tag.decompose()

	# Convert some <div>s to <p>s
	divs  = html.find_all("div", class_="separator")
	divs += html.find_all("div", class_="MsoNormal")
	divs += html.find_all("div", class_="Standard")
	divs += html.find_all("div", class_="p1")
	divs += html.find_all("div", class_="p3")
	for tag in divs:
		if tag.string:
			new_tag = html.new_tag("p")
			new_tag.string = tag.string
			tag.replace_with(new_tag)

	# Strip all unneeded <span> tags
	for tag in html.find_all('span'):
		if tag.string:
			tag.replace_with(tag.string)
		else:
			tag.decompose()

	current_paragraph = ""
	# Loop through all elements, switching between rich text and images as images are found

	for element in body:
		# Image detected
		if element.name == 'table' or (element.name == 'div' and len(element.find_all('img')) > 0):
			# if "current_paragraph" has any data, bank it as a rich text block
			if current_paragraph.strip() != "":
				content.append(content_block(current_paragraph))
				current_paragraph = ""

			# Add the image block to the content array
			table_images = element.find_all('img')
			if len(table_images) > 0:
				# Get the image src
				image = table_images[0]
				src = parse_image(image.get('src', ''))

				# Extract caption rich text from table cells
				cells = element.find_all('td')
				caption = ''

				# Clean up the caption HTML
				for td in cells:
					if len(td.get_text(strip=True)) > 0:
						for tag in td.find_all("div", class_="media"):
							tag.decompose()
						for c in td.contents:
							caption += str(c).strip()

				# One last find+replace on the caption for good measure
				caption = caption.replace("<table><tbody><tr><td></td></tr></tbody></table>","")

				# Add the image + caption to the content array
				content.append({
					'type': 'image',
					'data': {
						'src': src,
						'caption': caption,
					}
				})
		# Regular HTML content
		else:
			html_string = ""
			try:
				html_string = str(element).replace('\n','')
			except:
				# Can't prettify - probably a comment
				if "Comment" not in str(type(element)):
					print("WARNING: Couldn't parse content element:", element)

			current_paragraph += html_string

	# add one last rich text block if there is content at the end of the loop
	if current_paragraph.strip() != "":
		content.append(content_block(current_paragraph))

	return content

# ============ Create Assets =============

def download_external_image(url, file_name):
	local_path = "drupalimport/images/{}".format(file_name)
	# Only download if the file doesn't already exist
	if not os.path.isfile(local_path) and 'gamestop.com' not in url:
		try:
			print("Downloading...", file_name)
			urllib.request.urlretrieve(url, local_path)
		except Exception as e:
			print("EXCEPTION", e)
			print("URL:",url)

def parse_external_image(path):
	# Parse the URL out of these weird blogger modals
	if 'proxy' in path:
		path = path.replace('https://images-blogger-opensocial.googleusercontent.com/gadgets/proxy?url=', '')
		path = path.replace('&container=blogger&gadget=a&rewriteMime=image%2F*', '')
		path = path.replace('%2F','/') # Unencode slashes so we can parse out the file name

	url       = path.replace('%3A',':', 1) # ie 'http%3A//'
	file_name = urllib.parse.unquote(url.split('/')[-1])  # Un-URL-encode the actual image name

	# These are weird old blogger links that don't have file extensions.
	# The file names are super long randomized strings.
	# All of them are jpg's
	if '.png' not in file_name and '.jpg' not in file_name and '.JPG' not in file_name and '.jpeg' not in file_name and '.png' not in file_name:
		file_name = file_name + '.jpg'

	# Commented out since I've grabbed all the non-404 images i can from this
	# download_external_image(url, file_name)

	return file_name

# Remove path / url to image if it is from spritesanddice
# External images will need to be downloaded
def parse_image(path):
	if 'http' in path and 'spritesanddice' not in path:
		return parse_external_image(path)

	path = path.replace("/sites/default/files/","")
	path = path.replace("https://spritesanddice.com","")
	path = path.replace("http://www.spritesanddice.com","")
	path = path.replace("https://www.spritesanddice.com","")

	return urllib.parse.unquote(path)

def parse_podcast_mp3(path):
	filename = path.replace("https://www.spritesanddice.com/sites/default/files/podcast/episodes/","")
	filename = urllib.parse.unquote(filename)
	return filename

# ============ Main Script =============

wagtail_page_model = {}

def init():
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
		content = parse_drupal_body(n['body'])

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
			'header_video': n['field_video_embed_video_url'],

			'header':    parse_image(n['field_image']),
			'title':     n['title'],
			'subtitle':  n.get('field_subtitle', ''),

			'content': content, # An array of rich text / image blocks. to be converted in import_pages.py

			'author_id': convert_author_id(n['uid']),
			'slug':      convert_path_to_slug(n['path']),

			'tags': tags,

			'legacy_url':       n['path'],
			'post_datetime':    n['created'],
			'revised_datetime': n['changed'],

			# Fill these out later
			'game':    None,
			'podcast': None,
		}

		# CREATE PODCAST
		if n['field_show_podcast_player'] and n['field_podcast_title']:
			wagtail_page['podcast'] = {
				'title':          n['field_podcast_title'],
				'episode_number': n['field_episode_number'],
				'podcast_file':   parse_podcast_mp3(n['field_podcast_mp3']),
				'description':    n['field_podcast_description'],
				'publish_date':   n['created'], # parse date in import_pages
			}

		# CREATE GAME
		if n['field_game_name']:
			# Map old field names to new field names
			wagtail_page['game'] = {
				'title':             n['field_game_name'],
				'author':            n['field_author'],
				'developer':         n['field_developer'],
				'publisher':         n['field_publisher'],
				'platforms':         n['field_platforms'],
				'format':            n['field_format'],
				'number_of_players': n['field_number_of_players'],
				'play_time':         n['field_playing_time'],
				'price':             n['field_msrp'],
				'release_date':      n['field_release_date'], # parse date in import_pages
				'other_info':        n['field_other_info']    # needs to be split up into OtherInfo objects, do this in import_pages
			}

		pages.append(wagtail_page)

	print("Saving...")

	print("Saved {} pages".format(len(pages)))
	save_json(PAGE_JSON, pages)

	print("Done!")

# ======== Django Management Command =========

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = "Convert exported Drupal JSON to Django Fixtures"

	def handle(self, *args, **options):
		init()
