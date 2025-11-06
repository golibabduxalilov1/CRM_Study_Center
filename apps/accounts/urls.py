from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("otp/verify/", views.verify_otp, name="verify_otp"),
    path("logout/", views.logout, name="logout"),
    path(
        "allowlist/", views.AllowedEmailListCreateView.as_view(), name="allowlist-list"
    ),
    path(
        "allowlist/<int:pk>/",
        views.AllowedEmailDestroyView.as_view(),
        name="allowlist-delete",
    ),
    path("users/<str:role>/", views.UserListView.as_view(), name="users-by-role"),
    path("users/", views.UserListView.as_view(), name="users-list"),
]
