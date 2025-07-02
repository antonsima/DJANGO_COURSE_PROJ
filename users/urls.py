from django.urls import path

from .views import CustomSignupView

urlpatterns = [
    path("signup/", CustomSignupView.as_view(), name="signup"),
]