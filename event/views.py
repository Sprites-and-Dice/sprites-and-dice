from django.shortcuts import render

from .models import Event

def events_calendar(request):
	return render(request, 'event/calendar.html', {
		'events': Event.objects.all().order_by('start_date')
	})
