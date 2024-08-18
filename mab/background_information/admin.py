from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(PrivatePerson)
class PrivatePersonAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = ('id', 'firstname', 'lastname', 'middlename')

#admin.site.register(PrivatePerson)
admin.site.register(UtilityService)
admin.site.register(UnitsOfMeasures)
