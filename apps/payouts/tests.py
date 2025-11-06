from django.test import TestCase
from decimal import Decimal
from datetime import datetime
from apps.payouts.services import PayoutService
from django.contrib.auth import get_user_model
from apps.groups.models import Group
from apps.payments.models import Payment, CommissionSetting
from apps.students.models import Student

User = get_user_model()


class PayoutTest(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            username="mentor@test.com",
            email="mentor@test.com",
            password="testpass123",
            role="MENTOR",
        )

        self.student = Student.objects.create(
            first_name="Test",
            last_name="Student",
            email="student@test.com",
            phone="123456789",
        )

        self.group = Group.objects.create(
            name="Test Group",
            subject="Math",
            start_date="2024-01-01",
            end_date="2024-12-31",
            mentor=self.mentor,
            price_per_month=Decimal("1000000"),
        )

    def test_payout_calculation_default_commission(self):
        CommissionSetting.objects.create(
            type="GLOBAL",
            mentor_percentage=Decimal("60.00"),
            center_percentage=Decimal("40.00"),
        )

        Payment.objects.create(
            student=self.student,
            group=self.group,
            amount=Decimal("1000000"),
            due_date="2024-01-31",
            status="PAID",
            paid_at="2024-01-15",
        )

        calculation = PayoutService.calculate_mentor_payout(self.mentor, 2024, 1)

        self.assertEqual(calculation["total_collected"], Decimal("1000000"))
        self.assertEqual(calculation["mentor_share"], Decimal("600000"))
        self.assertEqual(calculation["center_share"], Decimal("400000"))
