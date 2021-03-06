function addEndMarkIcon(){
	let last_paragraph = $('.blog-page .blog-post-content > .rich-text').last().find('p').last();
	let p_not_empty = $.trim(last_paragraph.html()).length;
	if (p_not_empty) {
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

function initFontAwesome(){
	// Prevents FA from converting <i> tags to <svg> and breaking CSS
	window.FontAwesomeConfig = { autoReplaceSvg: false };
}

$(document).ready(function(){
	initFontAwesome();
	addClassToYouTubeContainer();
	addEndMarkIcon();
	makeExternalLinksTargetBlank();
});
