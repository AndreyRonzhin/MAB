from django.contrib import admin

from .forms import AccrualServiceForm
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
    list_display = ('date', 'flat', 'meter_device', 'value')

@admin.register(StatisticInstrumentReadings)
class StatisticInstrumentReadingsAdmin(admin.ModelAdmin):
    list_display = ('date', 'flat', 'meter_device', 'count')


@admin.register(PersonalAccount)
class PersonalAccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'flat', 'is_active', 'closing_date')


@admin.register(ListOfService)
class ListOfServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceAction)
class ServiceActionsAdmin(admin.ModelAdmin):
    pass


@admin.register(AccrualService)
class AccrualServicesAdmin(admin.ModelAdmin):
    form = AccrualServiceForm
    list_display = ('company', 'date', 'apartment_block', 'entrance', 'flat', 'total', 'total_renewal')


@admin.register(SheetService)
class SheetOfServicesAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SheetService._meta.fields]


@admin.register(CompanyApartmentBlock)
class CompanyApartmentBlockAdmin(admin.ModelAdmin):
    list_display = ('date', 'apartment_block', 'company', 'is_active')
