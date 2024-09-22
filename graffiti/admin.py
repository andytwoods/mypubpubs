from django.contrib import admin
from .models import Headset, GraffitiImage, randcode


class HeadsetAdmin(admin.ModelAdmin):
    # Display settings
    list_display = ('vr_id', 'user', 'temp_code', 'created', 'modified')
    list_display_links = ('vr_id',)
    list_filter = ('user', 'created', 'modified')

    # Searchable fields
    search_fields = ('vr_id', 'temp_code')

    # Read-only fields
    readonly_fields = ('temp_code', 'created', 'modified')

    # Field grouping for better organization in the Admin form
    fieldsets = (
        (None, {
            'fields': ('vr_id', 'user')
        }),
        ('Code', {
            'fields': ('temp_code',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )

    # Optional: Custom save method for admin if needed
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If new object, set temp_code
            while True:
                temp_code = randcode()
                if not Headset.objects.filter(temp_code=temp_code).exists():
                    obj.temp_code = temp_code
                    break
        super().save_model(request, obj, form, change)


# Register the enhanced admin section
admin.site.register(Headset, HeadsetAdmin)


from django.contrib import admin
from .models import GraffitiImage


class GraffitiImageAdmin(admin.ModelAdmin):
    # Display settings
    list_display = ('url', 'headset', 'created', 'modified')
    list_display_links = ('url',)
    list_filter = ('created', 'modified', 'headset')

    # Searchable fields
    search_fields = ('url', 'headset__vr_id')

    # Read-only fields
    readonly_fields = ('created', 'modified')

    # Field grouping for better organization in the Admin form
    fieldsets = (
        (None, {
            'fields': ('url', 'image', 'headset')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )


# Register the enhanced admin section
admin.site.register(GraffitiImage, GraffitiImageAdmin)
