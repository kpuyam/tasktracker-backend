from django.contrib import admin

from .models import Project, Role, Task

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'owner')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'due_date', 'status', 'project', 'owner')
    list_filter = ('status', 'project')
    search_fields = ('description',)

admin.site.register(Role)
