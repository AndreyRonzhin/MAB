from django.contrib import admin

from .models import *

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    fields = ('date', 'service', 'rate')
    list_display = ('date', 'service', 'rate')

@admin.register(InstrumentReading)
class InstrumentReadingAdmin(admin.ModelAdmin):
    #fields = ('date', 'service', 'rate')
    list_display = ('date', 'flat', 'service', 'meter_device', 'value')