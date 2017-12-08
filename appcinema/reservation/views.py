#  Copyright (C) 2017
#      Jakub Krajniak (jkrajniak at gmail.com)
#
#  This file is part of appcinema.
#
#  appcinema is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  appcinema is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    blocked_seats = models.Reservation.active_reservations.filter(screening=screening_id).values(
        'start_seat_block', 'seat_block_size')

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

def get_history(request):
    reservations = models.Reservation.objects.filter(user=request.user).order_by('reservation_confirmed')
    return render(request, 'reservation/history.html', {'reservations': reservations})


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = models.Reservation.objects.all()
    serializer_class = serializer.ReservationSerializer

    def perform_create(self, serializer):
        return super(ReservationViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        serializer.save()  # update data
        # Gets the blocked seats. Do we really need to send everytime all blocked seats?
        screening = serializer.validated_data.get('screening')
        blocked_seats = models.Reservation.active_reservations.filter(
            screening=serializer.validated_data.get('screening')
        ).values('start_seat_block', 'seat_block_size')
        pusher_client = pusher.Pusher(
            app_id='441251',
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster='eu',
            ssl=True)
        output_data = {
            'blocked_seats': list(blocked_seats),
            'screening_id': screening.id
        }
        pusher_client.trigger('appcinema-reservation', 'blocked-seats', output_data)