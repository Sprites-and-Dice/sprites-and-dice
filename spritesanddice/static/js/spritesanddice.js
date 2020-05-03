// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	// $('.wagtail-userbar').detach().appendTo('header .userbar');
	$('.wagtail-userbar').detach().appendTo('nav .userbar-container ul');
})

function addEndMarkIcon(){
	let last_paragraph = $('.blog-page .blog-post-content .rich-text').last().find('p').last();
	// Don't add the end mark to empty p tags
	if($.trim(last_paragraph.html()).length){
		$(last_paragraph).append("&nbsp;<i class='endmark'></i>");
	}
}

function makeExternalLinksTargetBlank(){
	// Make all outgoing links open in a new tab
	$('a').each(function() {
		if( location.hostname === this.hostname || !this.hostname.length ) {
			return;
		} else {
			$(this).attr('target', '_blank');
		}
	});
}

// Make it easier to target rich text youtube embeds with CSS (kinda hacky)
function addClassToYouTubeContainer(){
	$('.blog-page .blog-post-content iframe').closest('div').addClass('embed')
}

$(document).ready(function(){
	// Prevents FA from converting <i> tags to <svg> and breaking CSS
	window.FontAwesomeConfig = { autoReplaceSvg: false }

	addClassToYouTubeContainer();
	addEndMarkIcon();
	makeExternalLinksTargetBlank();
});
