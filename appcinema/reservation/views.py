from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.response import Response

from . import models
from . import serializer


# Single-page view
def index(request):
    #available_screening = models.Screening.objects.filter(start_screening__gte=datetime.date.today())
    available_screening = models.Screening.objects.all()  # for debug list all
    return render(request, 'reservation/index.html', {'screening': available_screening})


def get_screening(request, screening_id):
    """Returns information about screening."""
    screening = models.Screening.objects.select_related('auditorium').select_related('movie').get(pk=screening_id)


    data = {
        'id': screening.id,
        'title': screening.movie.title,
        'auditorium_name': screening.auditorium.name,
        'total_num_seats': screening.auditorium.total_num_seats,
        'rows': screening.auditorium.nrows,

    }

    return JsonResponse(data)


class ScreeningViewSet(viewsets.ModelViewSet):
    """API endpoint for the screening."""
    #queryset = models.Screening.objects.filter(start_screening__gte=datetime.date.today())
    queryset = models.Screening.objects.all()
    serializer_class = serializer.ScreeningSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = models.Movie.objects.all()
    serializer_class = serializer.MovieSerializer


class AuditoriumViewSet(viewsets.ModelViewSet):
    queryset = models.Auditorium.objects.all()
    serializer_class = serializer.AuditoriumSerializer