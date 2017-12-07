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
            screening = data['screening']
            seat_block_size = data['seat_block_size']
            if seat_block_size < 0 or seat_block_size > 5:
                raise serializers.ValidationError('Wrong size of the seats block')
            start_seat_number = data['start_seat_block']
            # Get the maximum number of seats in the auditorium.
            auditorium = screening.auditorium
            if start_seat_number + seat_block_size > auditorium.total_num_seats:
                raise serializers.ValidationError('Wrong position of the seats block')

        # Validate the session time.


        return data

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Reservation
        fields = ('id', 'user', 'screening', 'reservation_start', 'reservation_confirmed',
                  'status', 'start_seat_block', 'seat_block_size')