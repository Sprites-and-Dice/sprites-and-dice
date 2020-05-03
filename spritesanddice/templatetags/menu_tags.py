import pprint

from django import template
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.html import format_html

from home.models import HomePage
from image.models import CustomImage
from page.models import BasicPage, BlogPage, BlogFolder

from wagtail.users.models import UserProfile
from wagtail.core.models import Site, Page

register = template.Library()

# ======== Menus =========

@register.simple_tag(takes_context=True)
def main_menu(context):
	home_page  = context.request.site.root_page
	menu_pages = home_page.get_children().live().in_menu()
	return menu_pages

@register.simple_tag(takes_context=True)
def footer_menu(context):
	home_page  = context.request.site.root_page
	menu_pages = BasicPage.objects.child_of(home_page).live().in_menu()
	return menu_pages

# Base "Blog Feed" to be used by all feed templates
@register.simple_tag(takes_context=True)
def blog_posts(context, blog_folder=None, tag=None, page_number=1):
	query = BlogPage.objects

	try:
		page_number = context.request.GET.get('page')
	except:
		pass

	if tag: # Tag is a slugified string
		query = query.filter(tags__slug__iexact=tag).distinct()
	if blog_folder: # Blog Folder is a BlogFolder page instance
		query = blog_folder.get_children().specific()

	# Order by manually set "Go Live At" date
	query = query.live().order_by('-go_live_at')

	# Pagination
	paginator = Paginator(query, 25)
	try:
		pages = paginator.page(page_number)
	except PageNotAnInteger: # First Page
		pages = paginator.page(1)
	except EmptyPage: # Last Page
		pages = paginator.page(paginator.num_pages)

	return pages

@register.inclusion_tag('navigation/sidebar-posts.html', takes_context=True)
def sidebar_posts(context):
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

	current_category = ''
	if context.get('page') and type(context.get('page')) == BlogFolder:
		current_category = context['page'].title
	elif context.get('tag_name'):
		current_category = "TAG"+context['tag_name']

	return {
		'current_category': current_category,
		'context':          context,
		'categories':       tags + list(folders),
	}


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

@register.simple_tag()
def get_raw(value):
	return get_raw_response(value)

# ======== Filter Tags =========

# In: Int
# Out: List range X -> Int
@register.filter()
def loop_int(number, start_at_zero=False):
	if(start_at_zero):
		return range(number)
	else:
		return range(1, number+1)

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
