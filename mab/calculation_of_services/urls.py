from django.urls import path
from . import views

app_name = "calculation"

urlpatterns = [
    path('', views.СustomersHome.as_view(), name='home'),
    path('addreadings', views.AddReadings.as_view(), name='addReadings'),
    path('addreadingsnew', views.add_readings_new, name='addReadingsNew'),
]
