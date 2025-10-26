from rest_framework import serializers
from .models import Student
from apps.groups.models import Enrollment


class StudentSerializer(serializers.ModelSerializer):
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_enrollments_count(self, obj):
        return obj.enrollment_set.filter(status="ACTIVE").count()


class StudentDetailSerializer(StudentSerializer):
    enrollments = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ("enrollments",)

    def get_enrollments(self, obj):
        from apps.groups.serializers import EnrollmentSerializer

        enrollments = obj.enrollment_set.select_related("group").all()
        return EnrollmentSerializer(enrollments, many=True).data
