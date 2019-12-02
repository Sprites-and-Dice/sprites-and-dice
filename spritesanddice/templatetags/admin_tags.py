from django import template

from game.models import Game, ReviewCodes

register = template.Library()

@register.inclusion_tag('wagtailadmin/review_codes.html')
def review_codes():
	games = filter(lambda game: game.available_codes() > 0, Game.objects.all())
	return { 'games': games }
