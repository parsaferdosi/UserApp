from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("login/authorization/", views.AuthorizationView.as_view(), name="login_authorization"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/delete_account/", views.DeleteAccountView.as_view(), name="delete_account"),
    path("token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
]
