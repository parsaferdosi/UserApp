from django.urls import path

from . import views

urlpatterns=[
    path("register/",views.RegisterView.as_view(),name='register'),
    #path("login",views.LoginView.as_view(),name='login),
    #path("login/authoratazion/",views.AuthoratazionView.as_view(),name="login_authoratazion"),
    path("profile/",views.ProfileView.as_view(),name="profile"),
    path("profile/delete_account/",views.DeleteAccountView.as_view(),name="delete_account"),
]