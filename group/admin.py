from django.contrib import admin

from group.models import Group, GroupUserThru, GroupAdminThru, DomainNames


class GroupUserThruInline(admin.TabularInline):
    model = GroupUserThru
    extra = 1  # how many rows to show


class GroupAdminThruInline(admin.TabularInline):
    model = GroupAdminThru
    extra = 1  # how many rows to show


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", 'uuid', )
    inlines = (GroupUserThruInline, GroupAdminThruInline,)


admin.site.register(Group, GroupAdmin)


class DomainNamesAdmin(admin.ModelAdmin):
    list_display = ('domain', )

admin.site.register(DomainNames, DomainNamesAdmin)
