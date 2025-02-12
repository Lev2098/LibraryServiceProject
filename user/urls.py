from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from user.views import CreateUserView, ManageUserView, GoogleView

app_name = 'user'

urlpatterns = [
    # Default django user
    path("register/", CreateUserView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
    # JWT TOKEN
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # GOOGLE TOKEN
    path("google/", GoogleView.as_view(), name="google_auth"),

]