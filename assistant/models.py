from django.conf import settings
from django.db import models


class ChatMessage(models.Model):  # one message of the follow-up chat about an analysis
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    analysis = models.ForeignKey(
        "analyses.Analysis",
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Analysis {self.analysis_id} - {self.role}"
