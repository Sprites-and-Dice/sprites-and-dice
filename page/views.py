from django.shortcuts import redirect, render

from page.models import BlogPage, PageTag

def tag_page(request, tag_slug=''):
	tag = tag_slug.replace('-', ' ') # Un-slugify
	return render(request, 'page/tag_page.html', {
		'title': 'Pages tagged "{}"'.format(tag),
		'tag': tag,
		'tagged_pages': BlogPage.objects.filter(tags__name__iexact=tag).live().order_by('-last_published_at'), # Case-insensitive
	})
