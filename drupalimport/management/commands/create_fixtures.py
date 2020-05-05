from bs4 import BeautifulSoup, Comment, NavigableString
from pprint import pprint
from django.utils.html import format_html

import urllib, os, re

# ============ Handle JSON Files =============

import json

# Paths for input/output
DRUPAL_JSON = 'drupalimport/data/export-data.json'
PAGE_JSON   = 'drupalimport/data/pages.json'

def open_json(file_path):
	with open(file_path) as json_file:
		return json.load(json_file)

def save_json(file_path, data):
	with open(file_path, 'w') as json_file:
		json.dump(data, json_file, indent=4)

# ========== Conversion Functions ===========

def convert_author_id(drupal_author_id):
	authors = {
	# Drupal ----- Wagtail
		4:   		1, 		# "Jon Glover",
		3:   		2, 		# "Wyatt Krause",
		6:   		3, 		# "Adam Factor",
		9:   		4, 		# "Eric Henn",
		111: 		5, 		# "Otto Kratky",
		133: 		6, 		# "Shanna Wynn-Shirreffs",

		99:  		7,  	# "Peri Akman",
		102: 		8,  	# "Alex Ellick",
		110: 		9,  	# "Nate Brogan",
		122: 		10, 	# "Brandon Doerrer",
		128: 		11, 	# "Janene Andersen",
		134: 		12, 	# "Alton Campbell",
		92:  		13, 	# "Milo Axelrod",
		91:  		14, 	# "Reid Marshall",
		5:   		15, 	# "Dana Kjolner",
		7:   		16, 	# "Brandon Missig",
		8:   		17, 	# "Miranda Waterman",
		10:  		18, 	# "Ben Mayer",
		87:  		19, 	# "Bryan Isaia",
		143: 		20, 	# "Jessica Fisher",
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

# Clean up YouTube URLs
def parse_youtube_link(url):
	# Draftail uses youtube "watch" URLs for embeds
	# Convert "embed" URLs to regular URLs
	if 'youtube.com/embed' in url:

		url = url.replace("?feature=player_embedded","")
		video_id = url.split('/')[-1]
		url = "https://youtube.com/watch?v={}".format(video_id)

	return url

def create_image_title(src, alt=""):
	new_title = ""

	# Alt title is unique and not a file name
	if alt and alt.strip() != '' and alt.strip() != src.strip():
		new_title = alt
	# Alt title is missing or matches the file name
	else:
		new_title = src
		# Make the title human-readable and remove file extensions
		new_title = re.sub('.jpg',  '', new_title, flags=re.IGNORECASE)
		new_title = re.sub('.jpeg', '', new_title, flags=re.IGNORECASE)
		new_title = re.sub('.png',  '', new_title, flags=re.IGNORECASE)
		new_title = re.sub('.gif',  '', new_title, flags=re.IGNORECASE)
		new_title = new_title.replace('-',' ').replace('_',' ') # It's hard to search slugified file names - make them into spaces

	return new_title

# Convert a list of BeautifulSoup elements to a Rich_text stream block with a HTML formatted string
def content_block(elements):
	html_string = clean_up_rich_text(elements)
	if html_string.strip() != '':
		return {
			'type': 'rich_text',
			'data': html_string
		}

# Create an image block
# Only provide one image tag, and the element the image was a part of
# element contents will become the caption
def image_block(image, element):
	# Get image attributes from the <img> tag
	src   = parse_image(image.get('src', ''))
	alt   = image.get('alt')
	title = create_image_title(src, alt)
	# Remove all image tags from the caption
	for tag in element.find_all('img'):
		tag.decompose()
	return {
		'type': 'image',
		'data': {
			'title':   title,
			'alt':     alt,
			'src':     src,
			'caption': clean_up_rich_text([element]),
		}
	}

# Extract image blocks with captions from elements that contain images
# If any content is found that should go before this block, return it with current_paragraph
def clean_up_image_block(element, current_paragraph):
	new_blocks  = []
	images      = []
	image_count = 0

	if element.name == 'img':
		images = [element]
	else:
		images = element.find_all('img')

	image_count        = len(images)
	unique_src_list    = list(set([image.get('src') for image in images]))
	unique_image_count = len(unique_src_list)

	# If there is more than one unique SRC in this list, post a warning
	if unique_image_count > 1:
		print("WARNING: More than one image here!", element)
	else:
		new_blocks.append(image_block(images[0], element))

	return new_blocks, current_paragraph

# Catch some specific typos caught in import tests
def fix_typos(html_string):
	html_string = html_string.replace("findyourself", "find yourself")
	return html_string

# Before a BeautifulSoup object gets converted to rich text, clean up any remaining junk
def clean_up_rich_text(elements):
	html_string = ""

	# Clean up elements and combine them into one string
	for element in elements:
		if type(element) != NavigableString:
			# <div> --> <p>
			if element.name == 'div' or element.name =='td':
				element.name = 'p'
			for tag in element.find_all('div') + element.find_all('td'):
				tag.name = 'p'
			# <i> --> <em>
			if element.name == 'i':
				element.name = 'em'
			for tag in element.find_all('i'):
				tag.name = 'em'

		html_string += str(element)

	# Remove any leftover table tags - if they made it to this point they are probably needlessly wrapped around something
	html_string = html_string.replace("<table>","").replace("</table>","")
	html_string = html_string.replace("<thead>","").replace("</thead>","")
	html_string = html_string.replace("<tbody>","").replace("</tbody>","")
	html_string = html_string.replace("<tr>",   "").replace("</tr>",   "")
	html_string = html_string.replace("<th>",   "").replace("</th>",   "")

	# Most <span> tags were for inline styles added by the WYSIWYG - replace with spaces so adjacent words don't get stuck together
	html_string = html_string.replace("<span>"," ").replace("</span>", " ")

	# BS4 leaves a bunch of <None> tags where removed elements are. may have to figure out if they're important.
	html_string = html_string.replace("<None></None>","")

	# Empty P tags get outta here
	html_string = html_string.replace("<p></p>","")

	# Newline characters be gone!
	html_string = html_string.replace("\n","")

	# String cleanup
	html_string = html_string.strip()           # Strip leading/trailing whitespace
	html_string = ' '.join(html_string.split()) # Ensure there is never more than one consecutive space
	html_string = fix_typos(html_string) # Content-specific string replacements

	return html_string

# Before even parsing through HTML content, remove the stuff that is 100% junk
# Returns a BeautifulSoup object
def clean_up_html(html_string):
	html = BeautifulSoup(html_string, "html5lib")

	# Remove all comments
	for element in html(text=lambda text: isinstance(text, Comment)):
		element.extract()

	# Remove excess tags wrapped around Blogger-formatted images and videos
	for tag in html.find_all(class_="media-element-container"):
		images = tag.find_all('img')
		videos = tag.find_all('video') # TODO: Turn these into MEDIA
		if images:
			tag.replace_with(images[0])
		else:
			tag.replace_with(videos[0])

	# Strip all unwanted attributes
	unwanted_attributes = [
		"align", "mozallowfullscreen", "webkitallowfullscreen",
		"style", "stlye", "dir", "border", "cellpadding", "cellspacing",
		"allow", "typeof", "allowfullscreen", "frameborder", "itemprop"
	]
	tags_to_remove_class_from = [
		'table', 'p', 'tr', 'td', 'tbody', 'thead', 'span'
	]
	for tag in html():
		for attribute in unwanted_attributes:
			del tag[attribute]
		if tag.name in tags_to_remove_class_from:
			del tag['class']
			del tag['id']

	# Remove a bunch of specific tags:
	tags_to_delete  = html.find_all("br")
	tags_to_delete += html.find_all("meta")
	tags_to_delete += html.find_all("h2", class_="element-invisible")
	tags_to_delete += html.find_all("a",  id_="more")
	for tag in tags_to_delete:
		tag.decompose()

	# Replace Blogger embed videos with <embed> tags
	for tag in html.find_all("object", class_="BLOGGER-youtube-video"):
		# Find the inner embed tag
		if tag.find('embed'):
			new_tag = html.new_tag("embed")
			new_tag.attrs['url']       = parse_youtube_link(tag.find('embed').attrs['src'])
			new_tag.attrs['embedtype'] = 'media' # Wagtail "Media" rich text feature
			tag.replace_with(new_tag)

	# Replace Youtube iFrames with <embed> tags
	for tag in html.find_all("iframe"):
		# print("IFRAME", tag)
		new_tag = html.new_tag("embed")
		new_tag.attrs['url']       = parse_youtube_link(tag.attrs['src'])
		new_tag.attrs['embedtype'] = 'media' # Wagtail "Media" rich text feature
		tag.replace_with(new_tag)

	# Do somethin' with twitter embeds
	for tag in html.find_all("blockquote", class_="twitter-tweet"):
		# print("TWEET", tag)
		pass

	# Swap .pull-quote for <blockquote>
	for tag in html.find_all(class_="pull-quote"):
		tag.name = 'blockquote'
		del tag['class']

	# Strip empty <p>'s and <div>'s
	for tag in html.find_all('p') + html.find_all('div'):
		if tag.string and tag.string.strip() == '':
			tag.decompose()

	# Convert <div>'s with specific styles applied to them into regular <p>'s
	divs  = html.find_all(class_="separator")
	divs += html.find_all(class_="MsoNormal")
	divs += html.find_all(class_="Standard")
	divs += html.find_all(class_="p1")
	divs += html.find_all(class_="p3")
	for tag in divs:
		tag.name = 'p'
		del tag['class']

	return html

# Recursive????
def parse_body_element(element, content, current_paragraph):
	# If an element has multiple images, pass its elements to this function
	images = []
	try:
		images = element.find_all('img')
	except:
		pass

	if element.title == 'img':
		images = [element]

	if len(images) == 1:
		# Retrieve rich text & image blocks from this element
		# update current_paragraph with any elements that need to go BEFORE the first image block in new_blocks
		new_blocks, current_paragraph = clean_up_image_block(element, current_paragraph)

		# if "current_paragraph" has any data, bank it as a rich text block before the next image block
		if len(current_paragraph) > 0:
			new_block = content_block(current_paragraph)
			if new_block:
				content.append(new_block)
				current_paragraph = []

		# Append any new blocks that were returned to the content list
		content += new_blocks

	# THE RECURSIVE PART - if there are multiple images, get more specific and loop through this elements contents
	elif len(images) > 1:
		for e in element.contents:
			content, current_paragraph = parse_body_element(e, content, current_paragraph)

	# No images, just regular rich text content
	else:
		current_paragraph.append(element)

	return content, current_paragraph

# Parse Drupal body HTML with BeautifulSoup
# Don't look at this code it's a goddamn nightmare
def parse_drupal_body(drupal_body):
	# Get a BeautifulSoup object with most junk data removed
	html = clean_up_html(drupal_body)
	body = html.body

	content = []           # To populate with Stream Block data
	current_paragraph = [] # Holds "chunks" of rich text as we loop - a list of BeautifulSoup elements

	# Loop through all elements, switching between rich text and images as images are found
	for element in body:
		content, current_paragraph = parse_body_element(element, content, current_paragraph)

	# If there is any left over paragraph content, add it now
	if len(current_paragraph) > 0:
		new_block = content_block(current_paragraph)
		if new_block:
			content.append(new_block)

	return content

# ============ Create Assets =============

# These images break the download script every time or just waste time waiting for their host to time out,
# list them here so we can replace them in the future.
known_missing_images = [
	'fh_campaign-raider-story.jpg',
	'momentsff7610.jpg',
	'1983-budget-home-school-math-life-skills-creative-teach-grades-4-12-board-game-d1ba4651f8ffea984c6b0165845795f7.jpg',
]

def download_external_image(url, file_name):
	local_path = "drupalimport/images/{}".format(file_name.strip())
	# Only download if the file doesn't already exist
	if not os.path.isfile(local_path) and file_name not in known_missing_images:
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


	url = path.replace('%3A',':', 1) # ie 'http%3A//'
	file_name = urllib.parse.unquote(url.split('/')[-1])  # Un-URL-encode the actual image name

	# Replace some bullshit in a few problem files
	file_name = file_name.replace('latest?cb=','')

	# These are weird old blogger links that don't have file extensions.
	# The file names are super long randomized strings.
	# Not all of them are .jpgs, but it seems to work. consider changing the file extension if the server tells you what type it is
	if '.png' not in file_name and '.jpg' not in file_name and '.JPG' not in file_name and '.jpeg' not in file_name and '.png' not in file_name:
		file_name = file_name + '.jpg'

	# Comment this out once you're sure you've grabbed all the images you need
	# download_external_image(url, file_name)

	return file_name

# Remove path / url to image if it is from spritesanddice
# External images will need to be downloaded
def parse_image(path):
	if 'http' in path and 'spritesanddice' not in path:
		return parse_external_image(path)

	path = path.replace("/sites/default/files/","")
	path = path.replace("sites/default/files/","")
	path = path.replace("blogger_importer/","")
	path = path.replace("https://spritesanddice.com","")
	path = path.replace("http://www.spritesanddice.com","")
	path = path.replace("https://www.spritesanddice.com","")

	return urllib.parse.unquote(path)

def parse_podcast_mp3(path):
	filename = path.replace("https://www.spritesanddice.com/sites/default/files/podcast/episodes/","")
	filename = urllib.parse.unquote(filename)
	return filename

def clean_up_page_tags(tags, page_title):
	# Add tags based on titles
	if 'review' in page_title.lower():
		tags.append("Review")
	if 'preview' in page_title.lower():
		tags.append("Preview")
	if 'podcast' in page_title.lower():
		tags.append("Podcast")

	# Rename duplicative tags (plural -> singular, inconsistent punctuation, etc)
	for i, tag in enumerate(tags):
		if tag == 'Features':
			tags[i] = "Feature"
		if tag == 'Reviews':
			tags[i] = "Review"
		if tag == 'Previews':
			tags[i] = "Preview"
		if tag == 'Interviews':
			tags[i] = 'Interview'
		if tag == 'RPGs':
			tags[i] = 'RPG'
		if tag == 'Humans vs. Zombies':
			tags[i] = 'Humans vs Zombies'
		if tag == 'Player Unknown\'s Battlegrounds' or tag == 'Playerunknown\'s Battlegrounds':
			tags[i] = 'PlayerUnknown\'s Battlegrounds'
		if tag == 'Tiny Build':
			tags[i] = 'tinyBuild'
		if tag == 'undefined':
			del tags[i]
		if tag == 'Way Forward':
			tags[i] = 'WayForward'
		if tag == 'XCOM2':
			tags[i] = 'XCOM 2'
		if tag == 'The Last of Us: Left Behind DLC':
			tags[i] = 'The Last of Us'
		if tag == 'D&D' or tag == 'D&amp;D':
			tags[i] = 'Dungeons and Dragons'

	# Remove duplicate items
	tags = list(set(tags))

	# Clean up strings
	for i, tag in enumerate(tags):
		tags[i] = tag.strip() # Remove whitespace
		tags[i] = tag.replace("'","").replace("&#039;","").replace("&amp;"," and ") # Remove characters that don't tag well

	return tags

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
		# Formatted as a string split by "%%"
		tags = []
		node_tags = n.get('field_tags')
		node_categories = n.get('field_categories')
		if node_tags:
			tags += node_tags.split('%%')
		if node_categories:
			tags += node_categories.split('%%')

		# Header Image
		header_src = parse_image(n['field_image'])
		header_image = {
			'src': header_src,
			'title': create_image_title(header_src)
		}

		subtitle = n.get('field_subtitle','')
		subtitle = subtitle.replace("&#039;","\u0027")

		# CREATE PAGE
		wagtail_page = {
			'header_video': n['field_video_embed_video_url'],

			'header':    header_image,
			'title':     n['title'],
			'subtitle':  n.get('field_subtitle', ''),

			'content': content, # An array of rich text / image blocks. to be converted in import_pages.py

			'author_id': convert_author_id(n['uid']),
			'slug':      convert_path_to_slug(n['path']),

			'tags': tags,

			'legacy_url':       n['path'],
			'post_datetime':    n['created'],

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
				'title':             n['field_game_name'].strip(),
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
			# Add the game name as a page tag
			if n['field_game_name'] not in wagtail_page['tags']:
				wagtail_page['tags'].append(n['field_game_name'].strip())
			# Auto-sort into video game / tabletop
			if 'Video Games' in wagtail_page['tags']:
				wagtail_page['game']['type'] = 'video-game'
			if 'Tabletop' in wagtail_page['tags']:
				wagtail_page['game']['type'] = 'tabletop-game'

		# Clean up tags
		wagtail_page['tags'] = clean_up_page_tags(wagtail_page['tags'], wagtail_page['title'])

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
