from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from info.models import Users, CoronaSymptoms


class AdminPage(UserAdmin):
    list_display = ('time_stamp', 'phone_number', 'county', 'arrived_recently')
    search_fields = ('phone_number',)

    fieldsets = (
        ('Site Users', {'fields': ('phone_number', 'county')}),
        ('Permissions', {'fields': ('is_admin',)})
    )

    ordering = ('phone_number',)
    list_filter = ('county',)

    filter_horizontal = ()


class CoronaSymptomsPage(admin.ModelAdmin):
    list_display = ('user', 'user_symptoms')
    search_fields = ('user__phone_number', 'user_symptoms')


admin.site.register(Users, AdminPage)
admin.site.unregister(Group)
admin.site.register(CoronaSymptoms, CoronaSymptomsPage)
