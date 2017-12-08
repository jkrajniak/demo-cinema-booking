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

import datetime
import math

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from . import tasks


class Auditorium(models.Model):
    name = models.CharField(max_length=255)
    nrows = models.IntegerField(verbose_name="Number of rows")
    total_num_seats = models.IntegerField(verbose_name="Total number of seats")

    @property
    def ncols(self):
        return math.ceil(self.total_num_seats / self.nrows)

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


CANCELED, TENTATIVE, CONFIRMED, BOOKED = range(-1, 3)
STATUS = (
    (CANCELED, "Canceled"),
    (TENTATIVE, "Tentative booked"),
    (CONFIRMED, "Confirmed"),
    (BOOKED, "Booked")
)


class ActiveReservationsManager(models.Manager):
    def get_queryset(self):
        """Returns either CONFIRMED, BOOKED reservations or TENTATIVE but not older than 2 min"""
        time_limit = datetime.datetime.now() - datetime.timedelta(seconds=settings.TENTATIVE_BOOKED_SEC)
        return super(ActiveReservationsManager, self).get_queryset().exclude(
            status=CANCELED).filter(
            (Q(reservation_start__gte=time_limit) & Q(status__gte=TENTATIVE)) | Q(status__gte=CONFIRMED))


class Reservation(models.Model):
    user = models.ForeignKey(User)
    screening = models.ForeignKey(Screening)
    status = models.IntegerField(choices=STATUS, default=CANCELED)
    reservation_start = models.DateTimeField(auto_now_add=True)
    reservation_confirmed = models.DateTimeField(blank=True, null=True)
    start_seat_block = models.IntegerField(default=0)
    seat_block_size = models.IntegerField(default=0)

    objects = models.Manager()
    active_reservations = ActiveReservationsManager()

    @property
    def list_of_seats(self):
        """Gets list of seats for reservation in the format: {seat number}{row name}"""
        output_list = []
        for s in range(self.start_seat_block, self.start_seat_block + self.seat_block_size, 1):
            row = int(math.floor(s / self.screening.auditorium.ncols))
            col = int(s - row * self.screening.auditorium.ncols + 1)
            output_list.append('{:d}{:c}'.format(col, 65 + row))
        return output_list


@receiver(pre_save, sender=Reservation)
def pre_save_reservation(sender, instance, *args, **kwargs):
    if instance.status == CONFIRMED:
        instance.reservation_confirmed = datetime.datetime.now()
        # TODO(jakub): add celery task to change statuses of reservations from CONFIRMED to BOOKED
        # tasks.change_reservation_status.apply_async((instance.id,), countdown=settings.BOOKED_SEC)
