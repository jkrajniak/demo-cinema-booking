from rest_framework import serializers

from . import models

class ScreeningSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Screening
        fields = ('movie', 'auditorium', 'start_screening', 'reserved_seats')

class AuditoriumSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Auditorium
        fields = ('name', 'nrows', 'total_num_seats')

class ReservationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """Validate the seat reserved block."""
        if 'seat_block_size' in data and 'start_seat_block' in data:
            print(data)
            screening = data['screening']
            seat_block_size = data['seat_block_size']
            start_seat_number = data['start_seat_block']
            # Get the maximum number of seats in the auditorium.
            auditorium = screening.auditorium
            if start_seat_number + seat_block_size > auditorium.total_num_seats:
                raise serializers.ValidationError('Wrong number of selected seats.')
        return data
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Reservation
        fields = ('id', 'user', 'screening', 'reservation_start',
                  'confirmed', 'start_seat_block', 'seat_block_size')