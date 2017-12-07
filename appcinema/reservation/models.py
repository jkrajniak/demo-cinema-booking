from django.db import models
from django.contrib.auth.models import User

class Auditorium(models.Model):
    name = models.CharField(max_length=255)
    nrows = models.IntegerField(verbose_name="Number of rows")
    total_num_seats = models.IntegerField(verbose_name="Total number of seats")

    def __str__(self):
        return '{} ({})'.format(self.name, self.total_num_seats)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    movie_length = models.IntegerField(help_text='Movie length (minutes)')

    def __str__(self):
        return '{} ({} min)'.format(self.title, self.movie_length)

class Screening(models.Model):
    movie = models.ForeignKey(Movie)
    auditorium = models.ForeignKey(Auditorium)
    start_screening = models.DateTimeField()
    
class Reservation(models.Model):
    CANCELED, TENTATIVE, CONFIRMED, BOOKED = range(-1, 3)
    STATUS = (
        (CANCELED, "Canceled"),
        (TENTATIVE, "Tentative booked"),
        (CONFIRMED, "Confirmed"),
        (BOOKED, "Booked")
    )
    
    user = models.ForeignKey(User)
    screening = models.ForeignKey(Screening)
    status = models.IntegerField(choices=STATUS, default=CANCELED)
    reservation_start = models.DateTimeField(auto_now_add=True)
    reservation_confirmed = models.DateTimeField(blank=True, null=True)
    start_seat_block = models.IntegerField(default=0)
    seat_block_size = models.IntegerField(default=0)    