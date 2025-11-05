from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("otp/verify/", views.verify_otp, name="verify-otp"),
    path("logout/", views.logout, name="logout"),
    path("allowlist/", views.AllowedEmailListCreateView.as_view(), name="allowlist"),
    path(
        "allowlist/<int:pk>/",
        views.AllowedEmailDestroyView.as_view(),
        name="allowlist-detail",
    ),
    path("users/<str:role>/", views.UserListView.as_view(), name="users-by-role"),
]
