// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	$('.wagtail-userbar').detach().appendTo('header .userbar');
	// $('.wagtail-userbar').detach().appendTo('nav ul:last-child()');
})

$(document).ready(function(){
	// Prevents FA from converting <i> tags to <svg> and breaking CSS
	window.FontAwesomeConfig = { autoReplaceSvg: false }
});
