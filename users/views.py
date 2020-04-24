from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

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

def user_page(request, username="jon"):
	print("user pageee")

	user = User.objects.filter(username=username).first()
	user_pages = BlogPage.objects.filter(author=user)

	return render(request, 'page/user_page.html', {
		'user': user,
		'user_pages': user_pages,
	})
