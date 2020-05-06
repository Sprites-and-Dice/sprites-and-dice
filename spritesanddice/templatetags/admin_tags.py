from django import template

from game.models import Game

from page.models import BlogFolder

register = template.Library()

@register.inclusion_tag('wagtailadmin/review_copies.html')
def review_copies():
	games = filter(lambda game: game.available_copies() > 0, Game.objects.all())
	return { 'games': games }

@register.simple_tag()
def folders():
	return BlogFolder.objects.all()
