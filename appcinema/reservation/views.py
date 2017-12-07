import pusher

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import viewsets

from . import models
from . import serializer


# Single-page view
def index(request):
    # available_screening = models.Screening.objects.filter(start_screening__gte=datetime.date.today())
    available_screening = models.Screening.objects.all()  # for debug list all
    return render(request, 'reservation/index.html', {'screening': available_screening})


def get_screening(request, screening_id):
    """Returns information about screening."""
    # TODO(jakub): perhaps this view could be replaced by REST API
    screening = models.Screening.objects.select_related('auditorium').select_related('movie').get(pk=screening_id)
    blocked_seats = models.Reservation.objects.filter(
        screening=screening_id
    ).exclude(status=models.Reservation.CANCELED).values('start_seat_block', 'seat_block_size')

    data = {
        'id': screening.id,
        'title': screening.movie.title,
        'movie_time': screening.start_screening,
        'auditorium_name': screening.auditorium.name,
        'auditorium_id': screening.auditorium.id,
        'total_num_seats': screening.auditorium.total_num_seats,
        'rows': screening.auditorium.nrows,
        'blocked_seats': list(blocked_seats)
    }
    return JsonResponse(data)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = models.Reservation.objects.all()
    serializer_class = serializer.ReservationSerializer

    def perform_create(self, serializer):
        return super(ReservationViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Gets the blocked seats. Do we really need to send everytime all blocked seats?
        blocked_seats = models.Reservation.objects.filter(
            screening=serializer.validated_data.get('screening')
        ).exclude(status=models.Reservation.CANCELED).values('start_seat_block', 'seat_block_size')
        pusher_client = pusher.Pusher(
            app_id='441251',
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster='eu',
            ssl=True)
        pusher_client.trigger('appcinema-reservation', 'blocked-seats', {'blocked_seats': list(blocked_seats)})