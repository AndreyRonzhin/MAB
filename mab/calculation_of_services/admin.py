from django.contrib import admin

from .models import *

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
    pass

@admin.register(ListOfService)
class ListOfServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(ServiceActions)
class ServiceActionsAdmin(admin.ModelAdmin):
    pass

@admin.register(AccrualOfServices)
class AccrualOfServicesAdmin(admin.ModelAdmin):
    pass

@admin.register(SheetOfServices)
class SheetOfServicesAdmin(admin.ModelAdmin):
    pass