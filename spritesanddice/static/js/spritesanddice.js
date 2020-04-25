// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	$('.wagtail-userbar').detach().appendTo('header .userbar');
	// $('.wagtail-userbar').detach().appendTo('nav ul:last-child()');
})

function addEndMarkIcon(){
	let last_paragraph = $('.blog-page .blog-post-content .rich-text').last().find('p');
	console.log(last_paragraph);
	$(last_paragraph).append("&nbsp;<i class='endmark'></i>");
}

$(document).ready(function(){
	// Prevents FA from converting <i> tags to <svg> and breaking CSS
	window.FontAwesomeConfig = { autoReplaceSvg: false }

	addEndMarkIcon();
});
