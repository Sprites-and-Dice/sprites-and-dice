from django import forms
from django.utils.translation import ugettext_lazy as _

from users.models import User

from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import RichTextFieldPanel

class AuthorBioForm(WagtailAdminModelForm):
	bio = RichTextField()

	class Meta:
		model = User
		fields = ("bio",)
