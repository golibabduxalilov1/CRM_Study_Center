from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime
from ..payments.models import Payment, CommissionSetting
from .models import MentorPayout


class PayoutService:
    @staticmethod
    def get_commission_percentage(mentor, group=None):
        if group:
            try:
                setting = CommissionSetting.objects.get(
                    type="GROUP", group=group, is_active=True
                )
                return setting.mentor_percentage
            except CommissionSetting.DoesNotExist:
                pass

        try:
            setting = CommissionSetting.objects.get(
                type="MENTOR", mentor=mentor, is_active=True
            )
            return setting.mentor_percentage
        except CommissionSetting.DoesNotExist:
            pass

        try:
            setting = CommissionSetting.objects.get(type="GLOBAL", is_active=True)
            return setting.mentor_percentage
        except CommissionSetting.DoesNotExist:
            return Decimal("60.00")

    @staticmethod
    def calculate_mentor_payout(mentor, year, month):
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()

        payments = Payment.objects.filter(
            group__mentor=mentor,
            status="PAID",
            paid_at__date__gte=start_date,
            paid_at__date__lt=end_date,
        ).select_related("group")

        total_collected = Decimal("0.00")
        mentor_share = Decimal("0.00")

        for payment in payments:
            commission_pct = PayoutService.get_commission_percentage(
                mentor, payment.group
            )
            payment_mentor_share = payment.amount * (commission_pct / 100)

            total_collected += payment.amount
            mentor_share += payment_mentor_share

        center_share = total_collected - mentor_share

        return {
            "total_collected": total_collected,
            "mentor_share": mentor_share,
            "center_share": center_share,
        }

    @staticmethod
    def generate_payout(mentor, year, month):
        month_date = datetime(year, month, 1).date()

        existing_payout = MentorPayout.objects.filter(
            mentor=mentor, month=month_date
        ).first()

        if existing_payout:
            return existing_payout

        calculation = PayoutService.calculate_mentor_payout(mentor, year, month)

        payout = MentorPayout.objects.create(
            mentor=mentor,
            month=month_date,
            total_collected=calculation["total_collected"],
            mentor_share=calculation["mentor_share"],
            center_share=calculation["center_share"],
        )

        return payout
