// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	$('.wagtail-userbar').detach().appendTo('nav ul');
})
