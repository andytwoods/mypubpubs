from django.contrib import admin

from .models import Participant



class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("created", "data", )


admin.site.register(Participant, ParticipantAdmin)

