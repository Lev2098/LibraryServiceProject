from django.urls import path
from payments.views import (
    PaymentListUserView,
    PaymentListAdminView,
    PaymentCreateView,
    PaymentDetailView,
    PaymentUpdateView,
    PaymentDeleteView,
)


urlpatterns = [

    path("user/", PaymentListUserView.as_view(), name="payment-user-list"),
    path("admin/", PaymentListAdminView.as_view(), name="payment-admin-list"),
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("<int:pk>/update/", PaymentUpdateView.as_view(), name="payment-update"),
    path("<int:pk>/delete/", PaymentDeleteView.as_view(), name="payment-delete"),

]

app_name = "payments"
