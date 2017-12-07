from rest_framework import serializers

from . import models


class SeatReservedSerializer(serializers.ModelSerializer):
    def validate(self, data):
        print(data['reservation'])
        reservation = data['reservation']
        seat_number = data['seat_number']
        start_seat_number = data['start_seat_number']
        # Get the maximum number of seats in the auditorium.
        auditorium = reservation.screening.auditorium
        if start_seat_number + seat_number > auditorium.total_num_seats:
            raise serializers.ValidationError('Wrong number of selected seats.')
        return data

    class Meta:
        model = models.SeatReserved
        fields = ('id', 'reservation', 'seat_number', 'start_seat_number')

class ScreeningSerializer(serializers.HyperlinkedModelSerializer):
    reserved_seats = SeatReservedSerializer(many=True)
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

class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    seat_reserved = SeatReservedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Reservation
        fields = ('id', 'user', 'screening', 'reservation_start', 'confirmed', 'seat_reserved')