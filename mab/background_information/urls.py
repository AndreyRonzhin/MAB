from django.urls import path
from .views import *


app_name = "background_information"

urlpatterns = [
    path('persone/', PrivatePersonViewSet.as_view()),
]
