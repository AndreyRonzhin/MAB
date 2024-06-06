from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

#admin.site.register(User, UserAdmin)

@admin.register(User)
class UserAdmin1(admin.ModelAdmin):
    pass
    #list_display = ('id', 'username', 'flat_id', 'personal_account_id')
