from django.db import models
from accounts.models import User
from institutions.models import Institution


class Notification(models.Model):
    """
    Unified notification/announcement model.
    Can target a specific user OR broadcast to an entire role group.
    Also serves as the Campus Notice board (replaces cms.Announcement).
    """

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    institution = models.ForeignKey(
        Institution, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications',
    )
    # Target: specific user or a whole role group (leave recipient blank to broadcast)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications',
        null=True, blank=True,
    )
    role_target = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Broadcast to all users with this role, e.g. STUDENT, FACULTY",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL,
    )
    is_read = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=True,
        help_text="Public notices appear on all relevant dashboards.",
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sent_notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.recipient.email if self.recipient else (self.role_target or 'All')
        return f"[{self.get_priority_display()}] {self.title} → {target}"
