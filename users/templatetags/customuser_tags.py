from django import template

register = template.Library()

@register.inclusion_tag('users/author.html')
def author(user=None):
	return {
		'user': user
	}

@register.inclusion_tag('users/author_bio.html')
def author_bio(user=None):
	return {
		'user': user
	}
