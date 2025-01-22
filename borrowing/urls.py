from django.urls import path


from borrowing.views import (

    BorrowingUserListView,
    BorrowingAdminListView,
    BorrowBookAddView,
    BorrowBookUpdateView,
    ReturnBookView,

    PaymentListUserView,
    PaymentListAdminView,
    PaymentCreateView,
    PaymentDetailView,
    PaymentUpdateView,

)


urlpatterns = [

    path("borrows/", BorrowingUserListView.as_view(), name="borrow-user-list"),
    path("borrows/admin/", BorrowingAdminListView.as_view(), name="borrow-admin-list"),
    path("borrows/create/", BorrowBookAddView.as_view(), name="borrow-create"),
    path("borrows/<int:pk>/update", BorrowBookUpdateView.as_view(), name="borrow-create"),
    path("borrows/<int:pk>/return", ReturnBookView.as_view(), name="borrow-return"),

    path('payments/', PaymentListUserView.as_view(), name='payment-user-list'),
    path('payments/admin/', PaymentListAdminView.as_view(), name='payment-admin-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<int:pk>/update/', PaymentUpdateView.as_view(), name='payment-update'),

]

app_name = "borrowing"
