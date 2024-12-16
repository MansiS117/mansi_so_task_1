from django.contrib import admin

from .models import Comment, Task, User


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name")
    list_display_links = ("id", "email", "first_name", "last_name")


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "due_date",
        "assigned_to",
        "assigned_by",
        "assigned_at",
        "priority",
        "status",
        "complete",
    )
    list_display_links = (
        "id",
        "title",
        "assigned_to",
        "assigned_by",
        "assigned_at",
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "task", "commented_by")
    list_display_links = ("id", "content", "task", "commented_by")


admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
