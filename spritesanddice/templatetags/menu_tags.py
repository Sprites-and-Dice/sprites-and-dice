from django import template

from page.models import BlogPage

register = template.Library()

# ======== Simple Tags =========

@register.simple_tag()
def get_vars(value):
	try:
		print(vars(value))
		return vars(value)
	except:
		try:
			print(dir(value))
			return dir(value)
		except:
			print(value)
			return value

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
