# Sprites and Dice Drupal 7 Data Importer

This Django app is designed to provide `manage.py` commands for importing data exported from the old Drupal 7 site in JSON format.

New BlogPages should be imported as child pages of a BlogFolder specified by the user. This way we can run tests on a single folder that can be deleted without accidentally populating the entire site with bad data.

## Step 1: Export data from Drupal

- Use the `Views Data Exporter` module to create a JSON-formatted view containing all pages and fields you want to export
- Store this JSON file in `/drupalimport/data/export-data.json`

## Step 2: Clean up exported JSON and prepare data for import

- The data we are importing needs to be split into multiple models:
	- page.BlogPage
	- image.CustomImage
	- podcast.Podcast
	- game.Game
- Each model needs its own "fixture". In the case of Wagtail, we can't actually use standard Django fixtures, so we're essentially cleaning up our exported data to make the import process a little easier.

- Run the command `./manage.py create_fixtures`
- This command will parse the export data and place fixture data in `/drupalimport/data/*.json`

## Step 3: Import into Wagtail with a `manage.py` command

- This is the part where we actually tap into Wagtail and import our data.

- `./manage.py import_images`
- `./manage.py import_games`
- `./manage.py import_podcasts`
- `./manage.py import_pages`
