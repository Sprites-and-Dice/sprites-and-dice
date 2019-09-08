from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html

from wagtail.admin.menu import MenuItem
from wagtail.core import hooks


# ==== Admin CSS ====

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href={}/>', static('/css/admin.css'))

# === Menu Items ===

# Hide "Snippets"
@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'snippets']

@hooks.register('register_admin_menu_item')
def register_color_menu_item():
	return MenuItem('Podcast', '/admin/snippets/podcast/podcast/', classnames='icon icon-site', order=400)
