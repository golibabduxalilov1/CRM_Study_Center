from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Payment, CommissionSetting
from .serializers import PaymentSerializer, CommissionSettingSerializer
from apps.core.permissions import IsBossOrAdmin, IsSuperAdminOrBoss


class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsBossOrAdmin]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["SUPERADMIN", "BOSS", "ADMIN"]:
            return Payment.objects.select_related("student", "group").all()
        elif user.role == "MENTOR":
            return Payment.objects.filter(group__mentor=user)
        return Payment.objects.none()

        return


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsBossOrAdmin]


@api_view(["PATCH"])
@permission_classes([IsBossOrAdmin])
def update_payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        new_status = request.data.get("status")

        if new_status == "PAID" and payment.status != "PAID":
            payment.paid_at = timezone.now()

        payment.status = new_status
        payment.notes = request.data.get("notes", payment.notes)
        payment.payment_method = request.data.get(
            "payment_method", payment.payment_method
        )
        payment.save()
        return Response(
            {
                "message": "To'lov holati yangilandi",
                "payment": PaymentSerializer(payment).data,
            }
        )
    except Payment.DoesNotExist:
        return Response({"error": "To'lov topilmadi"}, status=status.HTTP_404_NOT_FOUND)


class CommissionGlobalView(generics.RetrieveUpdateAPIView):
    serializer_class = CommissionSettingSerializer
    permission_classes = [IsSuperAdminOrBoss]

    def get_object(self):
        return super().get_object()
