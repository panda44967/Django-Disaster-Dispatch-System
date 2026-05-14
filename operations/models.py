from django.conf import settings
from django.db import models
from django.urls import reverse


class ResponderProfile(models.Model):
    """Stores role concept for general users (must be queryable from DB)."""

    ROLE_COMMAND = "command"
    ROLE_MEDICAL = "medical"
    ROLE_LOGISTICS = "logistics"
    ROLE_SHELTER = "shelter"

    ROLE_CHOICES = [
        (ROLE_COMMAND, "指揮中心人員"),
        (ROLE_MEDICAL, "醫療人員"),
        (ROLE_LOGISTICS, "物資人員"),
        (ROLE_SHELTER, "避難所人員"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="responder_profile",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "應變人員角色"
        verbose_name_plural = "應變人員角色"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Incident(models.Model):
    title = models.CharField(max_length=200, verbose_name="事件標題")
    category = models.CharField(max_length=50, verbose_name="事件分類")
    priority = models.IntegerField(verbose_name="優先等級")
    location = models.CharField(max_length=200, verbose_name="發生地點")
    description = models.TextField(verbose_name="事件描述")
    reporter = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="reported_incidents",
        verbose_name="通報者",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否仍在處理中")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("incident_detail", kwargs={"pk": self.pk})


class ResourceRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DELIVERED = "delivered"

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="resource_requests",
    )
    requested_by = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="resource_requests_made",
    )
    item_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20)
    is_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.item_name} x{self.quantity} ({self.incident.title})"


class ActionLog(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="action_logs",
    )
    actor = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="action_logs_performed",
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log #{self.pk} on {self.incident_id}: {self.note[:40]}"
