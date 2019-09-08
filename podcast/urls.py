from django.conf.urls import url

from . import views

app_name = 'podcast'
urlpatterns = [
    url(r'^podcast/podcast/$', views.list, name='list'),
    url(r'^podcast/Podcast/$', views.list, name='list'),
]
