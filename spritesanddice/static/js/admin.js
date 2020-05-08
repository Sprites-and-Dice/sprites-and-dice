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

$(document).ready(function(){
	siteSummaryCountUp();
});
