from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Student
from .serializers import StudentSerializer, StudentDetailSerializer
from .filters import StudentFilter
from apps.core.permissions import IsBossOrAdmin


class StudentListCreateView(generics.ListAPIView):
    queryset = Student.objects.select_related().all()
    serializer_class = StudentSerializer
    permission_classes = [IsBossOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["-created_at"]


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerializer
    permission_classes = [IsBossOrAdmin]
