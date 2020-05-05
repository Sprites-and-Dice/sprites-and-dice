from django.conf.urls import url

from . import views

app_name    = 'users'
urlpatterns = [
	url(r'^(?P<username>\w+)/', views.user_page, name='page'),
	url(r'', views.user_index, name='all_users'),
]
