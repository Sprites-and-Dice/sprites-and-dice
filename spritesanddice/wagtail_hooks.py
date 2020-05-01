from django.templatetags.static import static
from django.utils.html import format_html

from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.core import hooks


# ============ Admin CSS ============

@hooks.register('insert_global_admin_css')
def global_admin_css():
	return format_html('<link rel="stylesheet" href="{}"/>', static('/css/admin.css'))

# ============ Menu Items ============

# Hide Snippets and Files
@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
	menu_items[:] = [item for item in menu_items if item.name not in ['snippets', 'documents', 'media', 'images']]

# Create "Files" submenu
@hooks.register('register_admin_menu_item')
def register_files_submenu():
	return SubmenuMenuItem(
		'Files',
		Menu(
			register_hook_name='register_files_menu_item',
			construct_hook_name='construct_files_menu'
		),
		classnames='icon icon-image',
		order=200
	)

# Add a link to the Wagtaildocs editor's guide
@hooks.register('register_admin_menu_item')
def register_help_menu_item():
	return MenuItem('Editor\'s Guide', 'https://docs.wagtail.io/en/v2.8.1/editor_manual/index.html', classnames='icon icon-help', attrs={'target':'_blank'}, order=900000)

@hooks.register('register_files_menu_item')
def register_dashboard_menu_item():
	return MenuItem('Media', '/admin/media/', classnames='icon icon-media')

@hooks.register('register_files_menu_item')
def register_dashboard_menu_item():
	return MenuItem('Documents', '/admin/documents/', classnames='icon icon-doc-full-inverse')

@hooks.register('register_files_menu_item')
def register_dashboard_menu_item():
	return MenuItem('Images', '/admin/images/', classnames='icon icon-image')

@hooks.register('register_admin_menu_item')
def register_color_menu_item():
	return MenuItem('Podcast', '/admin/snippets/podcast/podcast/', classnames='icon icon-fa-headphones', order=400)

# =============== Rich Text ===============

@hooks.register('register_rich_text_features')
def register_center_feature(features):
	feature_name = 'center'
	type_ = 'center'
	tag = 'div'

	control = {
		'type':        type_,
		'label':       'C',
		'description': 'Center',
	}

	features.register_editor_plugin(
		'draftail', feature_name, draftail_features.InlineStyleFeature(control)
	)

	features.register_converter_rule('contentstate', feature_name, {
		'from_database_format': {'div[class]': InlineStyleElementHandler(type_)},
		'to_database_format': {
			'style_map': {
				type_: {
					'element': tag,
					'props': {
						'class': 'text-center',
					},
				},
			},
		},
	})

	features.default_features.append(feature_name)

@hooks.register('register_rich_text_features')
def register_block_quote_feature(features):
	feature_name = 'blockquote'
	type_ = 'blockquote'
	tag = 'div'

	control = {
		'type': type_,
		'icon': 'quote',
		'description': 'Block Quote',
	}

	features.register_editor_plugin(
		'draftail', feature_name, draftail_features.InlineStyleFeature(control)
	)

	features.register_converter_rule('contentstate', feature_name, {
		'from_database_format': {'div[class]': InlineStyleElementHandler(type_)},
		'to_database_format': {
			'style_map': { type_: { 'element': tag, }, },
		},
	})

	features.default_features.append(feature_name)
