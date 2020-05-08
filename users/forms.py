from django import forms
from django.utils.translation import ugettext_lazy as _

from users.models import User

from wagtail.admin.edit_handlers import RichTextFieldPanel
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.core.fields import RichTextField
from wagtail.users.forms import UserEditForm, UserCreationForm, AvatarPreferencesForm
from wagtail.users.models import UserProfile

from pprint import pprint

# For users to edit their own Bio in Account Settings
class AuthorBioForm(WagtailAdminModelForm):
	title = forms.CharField()
	bio   = RichTextField()

	show_email = forms.BooleanField(required=False, label="Show email publicly?")
	twitter    = forms.CharField(required=False, label="Twitter Username")
	website    = forms.URLField(required=False,  label="Personal Website")

	class Meta:
		model  = User
		fields = (
			"title",
			"bio",

			"show_email",
			"twitter",
			"website",
		)


# For admins to edit users' bios in the User Edit form
class CustomUserEditForm(UserEditForm):
	title = forms.CharField()
	bio   = RichTextField()

	show_email = forms.BooleanField(required=False, label="Show email publicly?")
	twitter    = forms.CharField(required=False,    label="Twitter Username")
	website    = forms.URLField(required=False,     label="Personal Website")

	avatar = forms.ImageField(required=False, label=_("Upload a profile picture"))

	# Use a custom save hook to save the submitted avatar to the User's UserProfile
	# since it's not accessible via the UserEditForm
	def save(self):
		user   = self.instance
		avatar = self.cleaned_data.get('avatar')

		if avatar:
			try: # Create New Profile
				profile = UserProfile.objects.get(user=user)
				profile.avatar = avatar
				profile.save()
			except: # Save new Profile
				profile = UserProfile(user=user, avatar=avatar)
				profile.save()

		user.save()
		super(CustomUserEditForm, self).save(commit=True)
		return user
