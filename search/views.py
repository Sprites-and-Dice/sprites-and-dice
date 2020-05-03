from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from page.models import BlogPage

from wagtail.core.models import Page
from wagtail.search.models import Query


def search(request):
	search_query = request.GET.get('query', None)
	page         = request.GET.get('page', 1)

	# Search
	if search_query:
		search_results = BlogPage.objects.live().order_by('-go_live_at').search(search_query)
		query          = Query.get(search_query)

		# Record hit
		query.add_hit()

	else:
		search_results = Page.objects.none()

	# Pagination
	paginator = Paginator(search_results, 25)

	try:
		search_results = paginator.page(page)
	except PageNotAnInteger:
		search_results = paginator.page(1)
	except EmptyPage:
		search_results = paginator.page(paginator.num_pages)

	return render(request, 'search/search.html', {
		'search_query':   search_query,
		'pages': search_results,
	})
