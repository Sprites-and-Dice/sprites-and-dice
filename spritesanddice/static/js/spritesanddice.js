// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	$('.wagtail-userbar').detach().appendTo('nav ul');
})

$(document).ready(function(){
	// Prevents FA from converting <i> tags to <svg> and breaking CSS
	window.FontAwesomeConfig = { autoReplaceSvg: false }
});
