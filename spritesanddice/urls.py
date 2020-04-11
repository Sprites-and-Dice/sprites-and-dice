from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from podcast import urls as podcast_urls
from podcast import views as podcast_views

from search import views as search_views

urlpatterns = [
	url(r'^django-admin/', admin.site.urls),

	url(r'^admin/snippets/', include(podcast_urls)),

	url(r'^admin/',     include(wagtailadmin_urls)),
	url(r'^documents/', include(wagtaildocs_urls)),

	url(r'^search/$', search_views.search, name='search'),

	url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

	url(r'^podcast\.xml$', podcast_views.get_podcast_feed, name='xml'),

	# For anything not caught by a more specific rule above, hand over to
	# Wagtail's page serving mechanism. This should be the last pattern in
	# the list:
	url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns

	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
