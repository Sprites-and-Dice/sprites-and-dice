from django.shortcuts import redirect, render

from page.models import BlogPage, PageTag, TagFolder

from taggit.models import Tag

def tag_index(request):
	return render(request, 'page/tag_index.html', {
		'title': 'Tags',
		'tags': Tag.objects.all().distinct().order_by('name')
	})


def tag_page(request, tag_slug=''):
	tag_name   = tag_slug.replace('-', ' ') # Un-slugify
	title      = 'Pages tagged "{}"'.format(tag_name)
	tag_folder = TagFolder.objects.filter(title__iexact=tag_name).first()

	if tag_folder:
			return render(request, 'page/tag_page.html', {
				'title':    tag_folder.title,
				'tag_name': tag_name,
				'tag_slug': tag_slug,
				'page':     tag_folder,
			})
	else:
		return render(request, 'page/tag_page.html', {
			'title':    title,
			'tag_name': tag_name,
			'tag_slug': tag_slug,
		})

def get_rss_feed(request):
	return render(request, 'rss.xml', {
		'pages': BlogPage.objects.live().public().order_by('-go_live_at')
	}, content_type='text/xml')
