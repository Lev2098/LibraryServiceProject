from django.urls import path


from borrowing.views import (

    BorrowingUserListView,
    BorrowingAdminListView,
    BorrowBookAddView,
    BorrowBookUpdateView,
    ReturnBookView,
    BorrowingDeleteView,

)


urlpatterns = [

    path("user/", BorrowingUserListView.as_view(), name="borrow-user-list"),
    path("admin/", BorrowingAdminListView.as_view(), name="borrow-admin-list"),
    path("create/", BorrowBookAddView.as_view(), name="borrow-create"),
    path("<int:pk>/update/", BorrowBookUpdateView.as_view(), name="borrow-update"),
    path("<int:pk>/return/", ReturnBookView.as_view(), name="borrow-return"),
    path("<int:pk>/delete/", BorrowingDeleteView.as_view(), name="borrow-delete"),

]

app_name = "borrowing"
