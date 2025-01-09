from django.urls import path
from . import views

app_name = "exchange"

urlpatterns = [
    path('list_apartment_block', views.ListApartmentBlockUserAPIView.as_view(), name='list_apartment_block'),
    path('instrument_reading/<int:id_apartment>', views.InstrumentReadingAPIView.as_view(), name='instrument_reading_detail'),
]
