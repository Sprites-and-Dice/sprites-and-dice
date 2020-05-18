const isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;

var scrollSpeed;
var transparentNav = false;

function showNav() {
	$('nav.navbar').removeClass('hidden');
}

function hideNav() {
	$('nav.navbar').addClass('hidden');
}

function initFixedNavbar() {
	$(document).bind('mousewheel DOMMouseScroll', function(e){
		scrollSpeed = e.originalEvent.wheelDelta || e.originalEvent.detail || 0;

		let down = scrollSpeed >= 1;
		let up   = scrollSpeed <= -1;
		if(!isFirefox){
			up   = scrollSpeed >= 1;
			down = scrollSpeed <= -1;
		}

		if (down)   { hideNav(); }
		else if(up) { showNav(); }
	});
}

function initHamburgerButton(){
	$('.mobile-menu-trigger').click(function(e){
		e.preventDefault();
		$('.mobile-drawer').addClass('active');
		$('.mobile-overlay').addClass('active');
	});
	$('.mobile-overlay').click(function(e){
		e.preventDefault();
		$('.mobile-drawer').removeClass('active');
		$('.mobile-overlay').removeClass('active');
	})
}

function placeUserBarInNav(){
	if($('.wagtail-userbar').length){
		$('.wagtail-userbar').detach().appendTo('nav .userbar-container ul');
	}
	// else {
	// 	$('nav .userbar-container').remove();
	// }
}

$(document).ready(function(){
	initHamburgerButton();
	initFixedNavbar();
});

// Rip the .wagtail-userbar out of its default location and append it to the nav
$(window).on('load', function(){
	placeUserBarInNav();
})
