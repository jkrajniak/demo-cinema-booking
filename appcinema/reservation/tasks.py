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

from celery.decorators import task
from celery.utils.log import get_task_logger

from django.conf import settings

from . import models

logger = get_task_logger(__name__)

@task(name='change_reservation_status')
def change_reservation_status(reservation_id):
    """Change status from CONFIRMED to BOOKED after n minutes"""
    reservation = models.Reservation.objects.get(pk=reservation_id)