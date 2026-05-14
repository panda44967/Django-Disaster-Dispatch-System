from django.contrib import admin

from .models import ActionLog, Incident, ResourceRequest, ResponderProfile


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "priority",
        "location",
        "reporter",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "priority", "is_active", "created_at")
    search_fields = ("title", "location", "description")
    autocomplete_fields = ("reporter",)


@admin.register(ResourceRequest)
class ResourceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "item_name",
        "quantity",
        "status",
        "is_urgent",
        "incident",
        "requested_by",
    )


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ("incident", "actor", "created_at", "note_preview")

    @admin.display(description="Note preview")
    def note_preview(self, obj):
        return (obj.note[:60] + "…") if len(obj.note) > 60 else obj.note


@admin.register(ResponderProfile)
class ResponderProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__username",)
