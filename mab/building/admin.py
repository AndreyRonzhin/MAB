from django.contrib import admin

from .models import *

admin.site.register(ApartmentBlock)
admin.site.register(Entrance)
# admin.site.register(Flat)
admin.site.register(MeterDevice)


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = ('id', 'number', 'entrance', 'area_of_apartments', 'owner')
