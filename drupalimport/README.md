# Sprites and Dice Drupal 7 Data Importer

This Django app is designed to provide `manage.py` commands for importing data exported from the old Drupal 7 site in JSON format.

New BlogPages should be imported as child pages of a BlogFolder specified by the user. This way we can run tests on a single folder that can be deleted without accidentally populating the entire site with bad data.

## Goals

- Store all legacy content in a consistent format
- Strip all junk HTML left over from Blogger and Drupal's WYSIWYG editors
- Clean up tags: Consolidate "Categories" and "Tags" together, and move to a folder-based system for major categories
- Preserve SEO, backlinks, and comments
- Archive and store all previously external images on the server
- Split up the old monolithic "Page" model from the old site into: Page, Image, Podcast, Game

## Step 1: Export data from Drupal

- Use the `Views Data Exporter` module to create a JSON-formatted view containing all pages and fields you want to export
- Store this JSON file in `/drupalimport/data/export-data.json`
- Use your favorite FTP client to download any existing images / media files from the Drupal server.
- Store images in `/drupalimport/images/` - Don't put anything into subfolders. The script will import images by file name.
- Store podcasts in `/drupalimport/media/`

## Step 2: Clean up exported JSON and prepare data for import

- The data we are importing needs to be split into multiple models:
	- page.BlogPage
	- image.CustomImage
	- podcast.Podcast
	- game.Game
- All non-page models will be created at the same time as the pages they are associated with, so they will be bundled within the page content.

- Run the command `./manage.py create_fixtures`
- This command will parse the export data and place fixture data in `/drupalimport/data/pages.json`
- Additionally, it will try to download all external images to `drupalimport/images`. If you are doing multiple test runs, remove this command after you're sure you've grabbed every image you can.

## Step 3: Import into Wagtail with a `manage.py` command

- Run the command `./manage.py import_pages`
