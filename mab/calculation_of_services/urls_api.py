from django.urls import path, include
from .views_api import *
from rest_framework import routers

app_name = "calculation_of_services_api"

router = routers.SimpleRouter()
router.register(r'personalaccount', PersonalAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
