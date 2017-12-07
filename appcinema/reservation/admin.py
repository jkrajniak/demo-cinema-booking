from django.contrib import admin

from . import models

admin.site.register(models.Auditorium)
admin.site.register(models.Movie)
admin.site.register(models.SeatReserved)
admin.site.register(models.Screening)
admin.site.register(models.Reservation)
