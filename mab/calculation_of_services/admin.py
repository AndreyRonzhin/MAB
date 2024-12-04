from django.contrib import admin

from .forms import AccrualOfServicesForm
from .models import *


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name', 'inn')
    list_display = ('name', 'inn')


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    fields = ('date', 'service', 'rate')
    list_display = ('date', 'service', 'rate')


@admin.register(InstrumentReading)
class InstrumentReadingAdmin(admin.ModelAdmin):
    pass
    #fields = ('date', 'service', 'rate')
    #list_display = ('date', 'flat', 'service', 'meter_device', 'value')


@admin.register(PersonalAccount)
class PersonalAccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'flat', 'is_active', 'closing_date')


@admin.register(ListOfService)
class ListOfServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceActions)
class ServiceActionsAdmin(admin.ModelAdmin):
    pass


@admin.register(AccrualOfServices)
class AccrualOfServicesAdmin(admin.ModelAdmin):
    form = AccrualOfServicesForm


@admin.register(SheetOfServices)
class SheetOfServicesAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SheetOfServices._meta.fields]