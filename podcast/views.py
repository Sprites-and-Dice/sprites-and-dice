from datetime import datetime, timedelta

from django.apps import apps
from django.contrib.admin.utils import quote, unquote
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from podcast.models import Podcast

from urllib.parse import urlencode

from wagtail.admin import messages
from wagtail.admin.edit_handlers import ObjectList, extract_panel_definitions_from_model_class
from wagtail.admin.forms.search import SearchForm
from wagtail.search.backends import get_search_backend
from wagtail.search.index import class_is_indexed
from wagtail.snippets.models import get_snippet_models
from wagtail.snippets.permissions import get_permission_name, user_can_edit_snippet_type
from wagtail.snippets.views import snippets

def get_podcast_feed(request):
	episodes = Podcast.objects.filter(publish_date__lte=datetime.now()).order_by('-episode_number')
	latest_episode = episodes.first()
	return render(request, 'podcast/podcast.xml', {
		'latest_episode': latest_episode,
		'episodes': episodes,
	}, content_type='text/xml')


def list(request, app_label='podcast', model_name='Podcast'):

	model = snippets.get_snippet_model_from_url_params(app_label, model_name)

	permissions = [
		get_permission_name(action, model)
		for action in ['add', 'change', 'delete']
	]
	if not any([request.user.has_perm(perm) for perm in permissions]):
		return permission_denied(request)

	items = model.objects.all().order_by('-episode_number')

	# Search
	is_searchable = class_is_indexed(model)
	is_searching = False
	search_query = None
	if is_searchable and 'q' in request.GET:
		search_form = SearchForm(request.GET, placeholder=_("Search %(snippet_type_name)s") % {
			'snippet_type_name': model._meta.verbose_name_plural
		})

		if search_form.is_valid():
			search_query = search_form.cleaned_data['q']

			search_backend = get_search_backend()
			items = search_backend.search(search_query, items)
			is_searching = True

	else:
		search_form = SearchForm(placeholder=_("Search %(snippet_type_name)s") % {
			'snippet_type_name': model._meta.verbose_name_plural
		})

	paginator       = Paginator(items, per_page=50)
	paginated_items = paginator.get_page(request.GET.get('p'))

	# Template
	if request.is_ajax():
		template = 'podcast/results.html'
	else:
		template = 'podcast/type_index.html'

	return render(request, template, {
		'model_opts':          model._meta,
		'items':               paginated_items,
		'can_change_snippets': request.user.has_perm(get_permission_name('change', model)),
		'can_add_snippet':     request.user.has_perm(get_permission_name('add',    model)),
		'can_delete_snippets': request.user.has_perm(get_permission_name('delete', model)),
		'is_searchable':       is_searchable,
		'search_form':         search_form,
		'is_searching':        is_searching,
		'query_string':        search_query,
	})
