from rest_framework import serializers
from .models import Group, Enrollment
from apps.students.serializers import StudentSerializer


class GroupSerializer(serializers.ModelSerializer):
    mentor_name = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_mentor_name(self, obj):
        return f"{obj.mentor.first_name} {obj.mentor.last_name}" if obj.mentor else None

    def get_students_count(self, obj):
        return obj.enrollment_set.filter(status="ACTIVE").count()


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ("enrolled_date", "created_at", "updated_at")

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_group_name(self, obj):
        return obj.group.name


class GroupDetailSerializer(GroupSerializer):
    enrollments = EnrollmentSerializer(
        many=True, read_only=True, source="enrollment_set"
    )

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + "enrollments"
