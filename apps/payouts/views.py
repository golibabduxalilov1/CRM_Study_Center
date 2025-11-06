from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from .models import MentorPayout
from .serializers import MentorPayoutSerializer
from .services import PayoutService
from apps.core.permissions import IsBossOrAdmin, IsMentor

User = get_user_model()


class MentorPayoutListView(generics.ListAPIView):
    serializer_class = MentorPayoutSerializer

    def get_queryset(self):
        user = self.request.user
        mentor_id = self.request.query_params.get("mentor_id")

        if user.role in ["SUPERADMIN", "BOSS", "ADMIN"]:
            queryset = MentorPayout.objects.select_related("mentor").all()
            if mentor_id:
                queryset = queryset.filter(mentor_id=mentor_id)
        elif user.role == "MENTOR":
            queryset = MentorPayout.objects.filter(mentor=user)
        else:
            queryset = MentorPayout.objects.none()

        month_param = self.request.query_params.get("month")
        if month_param:
            try:
                year, month = map(int, month_param.split("-"))
                month_date = datetime(year, month, 1).date()
                queryset = queryset.filter(month=month_date)
            except ValueError:
                pass

        return queryset.order_by("-month")


@api_view(["POST"])
@permission_classes([IsBossOrAdmin])
def generate_mentor_payout(request):
    mentor_id = request.data.get("mentor_id")
    month_param = request.data.get("month")

    try:
        mentor = User.objects.get(id=mentor_id, role="MENTOR")
        year, month = map(int, month_param.split("-"))

        payout = PayoutService.generate_payout(mentor, year, month)

        return Response(
            {
                "message": "Mentor to'lovi hisoblandi",
                "payout": MentorPayoutSerializer(payout).data,
            }
        )
    except User.DoesNotExist:
        return Response({"error": "Mentor topilmadi"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response(
            {"error": "Noto'g'ri sana formati"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PATCH"])
@permission_classes([IsBossOrAdmin])
def mark_payout_paid(request, payout_id):
    try:
        payout = MentorPayout.objects.get(id=payout_id)
        payout.status = "PAID"
        payout.paid_at = timezone.now()
        payout.payment_details = request.data.get("payment_details", {})
        payout.save()

        return Response(
            {
                "message": "To'lov holati yangilandi",
                "payout": MentorPayoutSerializer(payout).data,
            }
        )
    except MentorPayout.DoesNotExist:
        return Response({"error": "To'lov topilmadi"}, status=status.HTTP_404_NOT_FOUND)
