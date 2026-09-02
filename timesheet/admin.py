from django.contrib import admin

from timesheet.models import Project, TimeEntry


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    exclude = ['created_at', 'deleted_at']


admin.site.register(Project, ProjectAdmin)



class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_time', 'exit_time', 'duration')
    search_fields = ('user__username',)
    exclude = ['created_at', 'deleted_at']


admin.site.register(TimeEntry, TimeEntryAdmin)