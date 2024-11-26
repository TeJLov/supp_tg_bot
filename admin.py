from django.contrib import admin
from .models import SearchBotTK, SuppBotTableRequests, FeedBack, ChatMessages

@admin.register(ChatMessages)
class ChatMessagesAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "from_who", "sent"
    ]
    readonly_fields = [
        "from_who", "tg_userid",
        "sent", "edited", "message",
        "image", "video", "voice",
        "file", "caption"
    ]

@admin.register(SuppBotTableRequests)
class SuppBotTableRequestsAdmin(admin.ModelAdmin):
    list_display = [
        "id", "first_menu", "theme", "status",
        "date_start", "date_stop", "work_eval"
        ]
    fields = [
        "id", "status", "learner", "lead", "first_menu", "theme",
        "messages", "who_answered", "work_eval", "feedback",
        "date_start", "date_stop", "is_new_message", "is_work"
        ]
    readonly_fields = [
        "id", "first_menu", "theme", "messages", "work_eval",
        "feedback", "date_start", "date_stop", "is_new_message",
        "is_work"
        ]
    search_fields = ["id", "status"]
    ordering = ("status",)

@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = [
       "id", "full_name", "tg_username", "date_creat"
    ]
    readonly_fields = [
        "tg_username", "tg_userid", "date_creat", "messages"
    ]
    ordering = ("id",)

@admin.register(SearchBotTK)
class SearchBotTKAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
