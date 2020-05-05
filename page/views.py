from django.shortcuts import redirect, render

from page.models import BlogPage, PageTag

from taggit.models import Tag

def tag_index(request):
	return render(request, 'page/tag_index.html', {
		'title': 'Tags',
		'tags': Tag.objects.all().distinct().order_by('name')
	})


def tag_page(request, tag_slug=''):
	tag_name = tag_slug.replace('-', ' ') # Un-slugify
	return render(request, 'page/tag_page.html', {
		'title':    'Pages tagged "{}"'.format(tag_name),
		'tag_name': tag_name,
		'tag_slug': tag_slug,
	})

def get_rss_feed(request):
	return render('rss.xml', {
		'pages': BlogPage.objects.live().order_by('-go_live_at')
	})
