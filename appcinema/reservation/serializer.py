from rest_framework import serializers

from . import models


class SeatReserved(serializers.ModelSerializer):
    class Meta:
        model = models.SeatReserved
        fields = ('reservation', 'seat_number')

class ScreeningSerializer(serializers.HyperlinkedModelSerializer):
    reserved_seats = SeatReserved(many=True)
    class Meta:
        model = models.Screening
        fields = ('movie', 'auditorium', 'start_screening', 'reserved_seats')

class AuditoriumSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Auditorium
        fields = ('name', 'nrows', 'total_num_seats')

class MovieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Movie
        fields = ('title', 'description', 'movie_length')