from django import forms
from django.utils.translation import ugettext_lazy as _

from users.models import User

from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import RichTextFieldPanel

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
