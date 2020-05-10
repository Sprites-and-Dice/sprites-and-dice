import pprint

from django import template
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.html import format_html

from home.models import HomePage
from image.models import CustomImage
from page.models import BasicPage, BlogPage, BlogFolder, TagFolder

from wagtail.users.models import UserProfile
from wagtail.core.models import Site, Page

register = template.Library()

# ======== Menus =========

@register.simple_tag(takes_context=True)
def main_menu(context):
	home_page  = context.request.site.root_page
	menu_pages = home_page.get_children().specific().live().public().in_menu()
	return menu_pages

@register.simple_tag(takes_context=True)
def footer_menu(context):
	home_page  = context.request.site.root_page
	menu_pages = BasicPage.objects.child_of(home_page).live().public().in_menu()
	return menu_pages

# Base "Blog Feed" to be used by all feed templates
@register.simple_tag(takes_context=True)
def blog_posts(context, blog_folder=None, tag=None, user=None, page_number=1):
	query = BlogPage.objects

	try:
		page_number = context.request.GET.get('page')
	except:
		pass

	if tag: # Tag is a slugified string
		query = query.filter(tags__slug__iexact=tag).distinct()
	if user:
		query = query.filter(author=user)
	elif blog_folder: # Blog Folder is a BlogFolder page instance
		query = blog_folder.get_children().specific()

	# Order by manually set "Go Live At" date
	query = query.live().public().order_by('-go_live_at')

	# Pagination
	paginator = Paginator(query, 25)
	try:
		pages = paginator.page(page_number)
	except PageNotAnInteger: # First Page
		pages = paginator.page(1)
	except EmptyPage: # Last Page
		pages = paginator.page(paginator.num_pages)

	return pages

@register.inclusion_tag('navigation/sidebar_posts.html', takes_context=True)
def sidebar_posts(context):
	MAX_POSTS = 4 # Number of posts displayed per category
	home_page = context.request.site.root_page

	# root_pages = home_page.get_children().specific().live().public()
	root_pages = home_page.get_children().specific().live()
	categories = []

	# If you are viewing a category page, don't include that category in the sidebar
	current_category = ''
	if context.get('page') and type(context.get('page')) == BlogFolder:
		current_category = context['page'].title.lower()
	elif context.get('tag_name'):
		current_category = context['tag_name'].lower()

	# We can't filter by "show_in_sidebar" with a queryset, so build a list of category pages
	# Do this instead of using two querysets - this way, menu ordering is preserved
	for page in root_pages:
		if page.show_in_sidebar and page.title.lower() != current_category:
			categories.append(page)

	for category in categories:
		if type(category) == BlogFolder:
			category.children = category.get_children().specific()
		if type(category) == TagFolder:
			tag_name = category.tag.name
			category.children = BlogPage.objects.filter(tags__name=tag_name).distinct()

		# Apply filters that are common between both category models
		category.children = category.children.live().public().order_by('-go_live_at')[:MAX_POSTS]

	return {
		'context':    context,
		'categories': categories,
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
def unpluralize_category(value):
	if value[-1] == 's' and value != "News":
		return value[:-1]
	else:
		return value

@register.filter()
def replace(value, substring, new_value):
	return value.replace(substring, new_value)

# ======== Inclusion Tags =========
