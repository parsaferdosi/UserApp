from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user import views
#using DRF router to automatically generate URL patterns for the viewsets
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'myaccount',views.MyAccountViewSet,basename='myaccount')
router.register(r'admin/accounts',views.AdminAccountViewSet,basename='admin-accounts')
urlpatterns =router.urls + [
    # Define your URL patterns here
    path('login/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
]