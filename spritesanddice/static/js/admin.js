function siteSummaryCountUp(){
	$('.stats a span:not(.visuallyhidden)').each(function(){
		let span = $(this);
		$({ Counter: 0 }).animate({ Counter: $(span).text().replace(',','') }, {
			duration: 1000,
			easing: 'swing',
			step: function (){
				$(span).text(Math.ceil(this.Counter));
			}
		});
	});
}

// Append "Add Child" button to folder pages in page drawer
function pageExplorerDrawerAddChildButton(){
	$('.c-explorer__item').each(function(){
		let is_folder            = $(this).find('.icon-folder-inverse').length > 0;
		let has_add_child_button = $(this).find('.add-folder-child').length    > 0;
		if(is_folder && !has_add_child_button){
			let page_id     = $(this).find('.c-explorer__item__link').attr('href').replace('/admin/pages/','').replace('/','');
			let page_title  = $(this).find('.c-explorer__item__title').html();
			let last_button = $(this).find('.c-explorer__item__action').last();
			$(`
				<a class="c-explorer__item__action add-folder-child" href="/admin/pages/${page_id}/add_subpage/">
					<span>
						<span class="icon icon-fa-plus-circle" aria-hidden="true"></span>
						<span class="visuallyhidden">Add a child page to '${page_title}'</span>
					</span>
				</a>
			`).insertBefore(last_button);
		}
	});
}

$(document).bind('DOMSubtreeModified',function(){
	pageExplorerDrawerAddChildButton();
})

$(document).ready(function(){
	siteSummaryCountUp();
	pageExplorerDrawerAddChildButton();
});
