import pprint

from django import template
from django.utils.html import format_html

from home.models import HomePage
from image.models import CustomImage
from page.models import BlogPage, BlogFolder

from wagtail.users.models import UserProfile
from wagtail.core.models import Site, Page

register = template.Library()

# ======== Menus =========

@register.simple_tag(takes_context=True)
def main_menu(context):
	home_page  = context.request.site.root_page
	menu_pages = home_page.get_children().live().in_menu()
	return menu_pages

@register.simple_tag()
def blog_posts():
	return BlogPage.objects.live().order_by('-go_live_at')

@register.inclusion_tag('navigation/sidebar-posts.html')
def sidebar_posts():
	MAX_POSTS = 4 # Number of posts displayed per category

	# Get Tags
	tags = [{
		'title': 'Video Games',
		'src': '/static/img/icons/large/controller.png',
		'icon':  None,
		'url':   '/tags/video-games/',
	}, {
		'title': 'Tabletop',
		'src': '/static/img/icons/large/cards.png',
		'icon':  None,
		'url':   '/tags/tabletop/',
	}]

	for tag in tags:
		tag['children'] = BlogPage.objects.filter(tags__name=tag['title']).distinct().live().order_by('-go_live_at')[:MAX_POSTS]

	# Get Folders
	folders = BlogFolder.objects.live().in_menu()

	for folder in folders:
		folder.children  = folder.get_children().specific().live().order_by('-go_live_at')[:MAX_POSTS]

	return { 'categories': tags + list(folders), }


# ======== Simple Tags =========

def get_vars_response(value):
	pprint.pprint(vars(value))
	return format_html(
		'<pre>{}</pre>',
		pprint.pformat(vars(value), indent=4)
	)

def get_dir_response(value):
	pprint.pprint(dir(value))
	return format_html(
		'<pre>{}</pre>',
		pprint.pformat(dir(value), indent=4)
	)

def get_raw_response(value):
	pprint.pprint(value)
	return format_html(
		'<pre>{}</pre>',
		pprint.pformat(value, indent=4)
	)

@register.simple_tag()
def get_vars(value):
	try:
		return get_vars_response(value)
	except:
		try:
			return get_dir_response(value)
		except:
			return get_raw_response(value)

@register.simple_tag()
def get_dir(value):
	try:
		return get_dir_response(value)
	except:
		return get_raw_response(value)

# ======== Filter Tags =========

@register.filter()
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hr".format(int(hrs))
        secs = secs - hrs*3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} min".format(int(mins))
        secs = secs - mins*60

    if secs > 0:
        timetot += " {} sec".format(int(secs))
    return timetot

@register.filter()
def unpluralize_category(value):
	if value[-1] == 's' and value != "News":
		return value[:-1]
	else:
		return value

@register.filter()
def replace(value, substring, new_value):
	return value.replace(substring, new_value)

# ======== Inclusion Tags =========
