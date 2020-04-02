from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from wagtail.admin import messages

from users.forms import AuthorBioForm

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
