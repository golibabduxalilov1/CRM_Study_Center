from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from apps.core.models import AuditLog
from apps.notifications.utils import send_notification, send_dashboard_update


@receiver(post_save, sender=Payment)
def log_payment_changes(sender, instance, created, **kwargs):
    action = "CREATE" if created else "UPDATE"
    AuditLog.objects.create(
        user=getattr(instance, "_current_user", None),
        action=action,
        model_name="Payment",
        object_id=str(instance.id),
        details={
            "student": str(instance.student),
            "amount": str(instance.amount),
            "status": instance.status,
        },
    )

    if instance.status == "PAID" and not created:
        send_notification(
            instance.student.id,
            f"To'lovingiz qabul qilindi: {instance.amount} so'm",
            {"payment_id": instance.id},
        )

        send_dashboard_update(
            {
                "type": "payment_received",
                "amount": str(instance.amount),
                "student": str(instance.student),
            }
        )
