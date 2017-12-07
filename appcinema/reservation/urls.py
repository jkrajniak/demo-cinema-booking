from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('screenings', views.ScreeningViewSet)
router.register('movies', views.MovieViewSet)
router.register('auditoria', views.AuditoriumViewSet)
router.register('reservation', views.ReservationViewSet)
router.register('seatreserved', views.SeatReservedViewSet)

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'get_screening/(?P<screening_id>[0-9]+)/$', views.get_screening),
    url(r'reserve_seats/(?P<screening_id>[0-9]+)/$', views.reserve_seats),
    url(r'^api/', include(router.urls)),
]