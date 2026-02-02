from django.contrib import admin
from .models import ContactMessage, Task, ActivityLog


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'category', 'due_date', 'due_time', 'completed', 'created_at')
    list_filter = ('completed', 'priority', 'category', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'completed_at')
    date_hierarchy = 'due_date'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'action', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
