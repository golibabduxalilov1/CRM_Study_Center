from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from apps.payments.models import Payment
from apps.students.models import Student
from apps.groups.models import Group, Enrollment
from apps.payouts.models import MentorPayout
from django.contrib.auth import get_user_model

User = get_user_model()


class AnalyticsService:
    @staticmethod
    def get_revenue_summary(start_date=None, end_date=None):
        filters = Q(status="PAID")
        if start_date:
            filters &= Q(paid_at__date__gte=start_date)
        if end_date:
            filters &= Q(paid_at__date__lte=end_date)

        payments = Payment.objects.filter(filters)

        return {
            "total_revenue": payments.aggregate(total=Sum("amount"))["total"]
            or Decimal("0"),
            "payment_count": payments.count(),
            "average_payment": payments.aggregate(avg=Avg("amount"))["avg"]
            or Decimal("0"),
            "pending_amount": Payment.objects.filter(status="PENDING").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0"),
            "overdue_amount": Payment.objects.filter(status="OVERDUE").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0"),
        }

    @staticmethod
    def get_monthly_revenue_chart(months=12):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)

        payments = (
            Payment.objects.filter(
                status="PAID",
                paid_at__date__gte=start_date,
                paid_at__date__lte=end_date,
            )
            .extra(select={"month": "DATE_FORMAT(paid_at, '%%Y-%%m')"})
            .values("month")
            .annotate(revenue=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        return list(payments)

    @staticmethod
    def get_students_per_group():
        groups = Group.objects.annotate(
            active_students=Count("enrollment", filter=Q(enrollment__status="ACTIVE")),
            total_students=Count("enrollment"),
        ).values("name", "active_students", "total_students", "max_students")

        return list(groups)

    @staticmethod
    def get_mentor_performance():
        mentors = (
            User.objects.filter(role="MENTOR")
            .annotate(
                groups_count=Count("group"),
                total_students=Count(
                    "group__enrollment", filter=Q(group__enrollment__status="ACTIVE")
                ),
                total_revenue=Sum(
                    "group__payment__amount", filter=Q(group__payment__status="PAID")
                ),
            )
            .values(
                "id",
                "first_name",
                "last_name",
                "groups_count",
                "total_students",
                "total_revenue",
            )
        )

        return list(mentors)

    @staticmethod
    def get_payment_status_distribution():
        return (
            Payment.objects.values("status")
            .annotate(count=Count("id"), total_amount=Sum("amount"))
            .order_by("status")
        )

    @staticmethod
    def get_enrollment_trends(days=30):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        enrollments = (
            Enrollment.objects.filter(
                enrolled_date__gte=start_date, enrolled_date__lte=end_date
            )
            .extra(select={"date": "DATE(enrolled_date)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return list(enrollments)
