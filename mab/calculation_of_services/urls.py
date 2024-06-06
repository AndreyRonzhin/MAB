from django.urls import path
from . import views


app_name = "calculation"

urlpatterns = [
    path('', views.CustomersHome.as_view(), name='home'),
    path('showreadings', views.show_readings_new, name='showReadings'),
    path('addreadings', views.AddReadings.as_view(), name='addReadings'),
    path('addreadingsnew', views.add_readings_new, name='addReadingsNew'),
]
