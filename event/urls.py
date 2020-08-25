from django.urls import include, path, re_path

from . import views

app_name = 'event'

urlpatterns = [
	path('', views.events_calendar, name='calendar'),
]
