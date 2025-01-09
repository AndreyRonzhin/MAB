from django.urls import path
from . import views

app_name = "calculation"

urlpatterns = [
    path('', views.home, name='home'),
    path('customers', views.CustomersHome.as_view(), name='customers'),
    path('accruals', views.AccrualHome.as_view(), name='accruals'),
    path('showreadings', views.show_readings_new, name='showReadings'),
    path('addreadings', views.add_readings, name='addReadings'),
    path('createaccruals', views.create_accruals, name='createAccruals'),
    path('editaccruals/<int:id>', views.edit_accruals, name='editAccruals'),
    path('entrance_autocomplete', views.EntranceAutocompleteView.as_view(), name='entrance_autocomplete'),
]
