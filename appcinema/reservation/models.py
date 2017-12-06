from django.db import models

class Auditorium(models.Model):
    name = models.CharField(max_length=255)
    nrows = models.IntegerField(verbose_name="Number of rows")
    total_num_seats = models.IntegerField(verbose_name="Total number of seats")
    
class Seat(models.Model):
    row = models.IntegerField()
    seat_number = models.IntegerField()
    auditorium = models.ForeignKey(Auditorium)
    
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    movie_length = models.IntegerField()

class Screening(models.Model):
    movie = models.ForeignKey(Movie)
    auditorium = models.ForeignKey(Auditorium)
    start_screening = models.DateTimeField()
    
class Reservation(models.Model):
    # user = ...
    screening = models.ForeignKey(Screening)
    reservation_start = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField()