from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.db.models import Q

from wagtail.admin import messages

from users.forms import AuthorBioForm

from users.models import User

from page.models import BlogPage

def change_bio(request):
	if request.method == 'POST':
		form = AuthorBioForm(request.POST, instance=request.user)

		if form.is_valid():
			form.save()
			messages.success(request, _("Your bio has been changed successfully!"))
			return redirect('wagtailadmin_account')
	else:
		form = AuthorBioForm(instance=request.user)

	return render(request, 'wagtailadmin/account/change_bio.html', {
		'form': form,
	})

def user_index(request):
	users = User.objects.all()
	return render(request, 'users/user_index.html', { 'users': users })

def user_page(request, username=None):
	user = User.objects.filter(username=username).first()
	if user:
		return render(request, 'page/user_page.html', { 'user': user })

	# No username found, check if the URL matches a user's full name
	else:
		# Drupal-era user URLs were `/users/full-name-slug/`
		# attempt to un-slugify the username and search by full name
		first_name = username.split('-')[0]
		last_name  = ' '.join(username.split('-')[1:])

		# Some old last names have hyphens, so search for last names with spaces OR hyphens
		users = User.objects
		users = users.filter(first_name__iexact=first_name)
		users = users.filter(Q(last_name__iexact=last_name.replace(' ','-')) | Q(last_name__iexact=last_name))

		user = users.first()

		# 301 Redirect to the new /users/ URL
		if user:
			username = user.username
			return HttpResponseRedirect('/users/{}/'.format(username), status=301)
		# 302 Redirect to /users/ index
		else:
			return HttpResponseRedirect('/users/', status=302)
