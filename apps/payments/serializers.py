from rest_framework import serializers
from .models import Payment, CommissionSetting


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField()
    group_name = serializers.CharField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_group_name(self, obj):
        return obj.group.name


class CommissionSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionSetting
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        mentor_pct = attrs.get("mentor_percentage", 0)
        center_pct = attrs.get("center_percentage", 0)

        if mentor_pct + center_pct != 100:
            raise serializers.ValidationError(
                "Mentor va markaz foizlari yig'indisi 100% bo'lishi kerak"
            )
        return attrs
