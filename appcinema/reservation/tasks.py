from celery.decorators import task
from celery.utils.log import get_task_logger

from django.conf import settings

from . import models

logger = get_task_logger(__name__)

@task(name='change_reservation_status')
def change_reservation_status(reservation_id):
    """Change status from CONFIRMED to BOOKED after n minutes"""
    reservation = models.Reservation.objects.get(pk=reservation_id)