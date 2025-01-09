from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(PrivatePerson)
class PrivatePersonAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = ('id', 'firstname', 'lastname', 'middlename')


@admin.register(UtilityService)
class UtilityServiceAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'unit_of_measure', 'quantify', 'type_device')


admin.site.register(UnitsOfMeasures)
