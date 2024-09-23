"""
URL configuration for mab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


from building.views import *

api_v1_patterns = [
    path('', include('background_information.urls_api', namespace="background_information_api")),
    path('', include('calculation_of_services.urls_api', namespace="calculation_of_services_api"))
]

urlpatterns = [
    path('', include('calculation_of_services.urls', namespace="calculation")),
    path('background_information/', include('background_information.urls', namespace="background_information")),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace="users")),
    path('api/v1/', include(api_v1_patterns)),
    # path('api/v1/buildinglist/', ApartmentBlockViewSet.as_view({'get': 'list', 'post': 'create'})),
    # path('api/v1/buildinglist/<int:pk>/', ApartmentBlockViewSet.as_view({'get': 'retrieve'})),
    path("__debug__/", include("debug_toolbar.urls")),
]
