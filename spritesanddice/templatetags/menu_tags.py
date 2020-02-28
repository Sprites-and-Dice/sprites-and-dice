import pprint

from django import template
from django.utils.html import format_html

from page.models import BlogPage
from wagtail.users.models import UserProfile

register = template.Library()

# ======== Simple Tags =========

@register.simple_tag()
def get_vars(value):
	try:
		pprint.pprint(vars(value))
		return format_html(
			'<pre>{}</pre>',
			pprint.pformat(vars(value), indent=4)
		)
	except:
		try:
			pprint.pprint(dir(value))
			return pprint.pformat(dir(value), indent=4)

		except:
			pprint.pprint(value)
			return pprint.pformat(value, indent=4)

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


# ======== Inclusion Tags =========

@register.inclusion_tag('navigation/sidebar-posts.html')
def sidebar_posts(title, tag, icon=''):
	if icon:
		icon_url  = '/static/img/icons/small/{}.png'.format(icon)
		icon_name = icon.capitalize()
	else:
		icon_url  = ''
		icon_name = ''

	blog_posts = BlogPage.objects.filter(tags__name=tag)[:4]

	return {
		'icon_name':  icon_name,
		'icon_url':   icon_url,
		'title':      title,
		'blog_posts': blog_posts,
	}


@register.inclusion_tag('blocks/author.html')
def author(id):
	user = UserProfile.objects.get(id=id)
	return { 'user': user.user }
