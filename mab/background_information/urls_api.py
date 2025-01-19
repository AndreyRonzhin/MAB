from django.urls import path, include
from .views import *
from rest_framework import routers

app_name = "background_information_api"

router = routers.SimpleRouter()
router.register(r'persone', PrivatePersonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
