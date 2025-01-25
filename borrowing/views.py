from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowBookSerializer
)
from borrowing.services import borrow_book, returned_book
from user.models import User


class BorrowingUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get a list of all users payments"""
        borrow = Borrowing.objects.filter(user=request.user)
        serializer = BorrowingSerializer(borrow, many=True)
        return Response(serializer.data)


class BorrowingAdminListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """Get a list of all users payments"""
        borrow = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrow, many=True)
        return Response(serializer.data)


class BorrowBookAddView(APIView):
    permission_classes = (IsAdminUser,)

    @extend_schema(
        request=BorrowBookSerializer,
        examples=[
            OpenApiExample(
                "Example Body",
                value={
                    "user": 1,
                    "expected_return_date": "2025-01-25",
                    "book": 2

                },
                description=" You can borrowing book use this example !"
            )
        ]
    )

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user")

        book_id = request.data.get("book")
        expected_return_date = request.data.get("expected_return_date")

        if not book_id or not expected_return_date:
            return Response(
                {"error": "Both 'book_id' and 'expected_return_date' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            borrowing = borrow_book(user, book_id, expected_return_date)
            return Response(
                {"message": "Book borrowed successfully.", "borrowing_id": borrowing.id},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BorrowBookUpdateView(APIView):
    permission_classes = (IsAdminUser,)

    def put(self, request, *args, **kwargs):
        """
        Update borrowing record (e.g., change user, expected return date, or book).
        """
        borrowing_id = kwargs.get("pk")
        user_id = request.data.get("user")
        book_id = request.data.get("book")
        expected_return_date = request.data.get("expected_return_date")
        status = request.data.get("status")

        try:
            borrowing = Borrowing.objects.get(id=borrowing_id)
        except Borrowing.DoesNotExist:
            return Response({"error": "Borrowing not found."}, status=status.HTTP_404_NOT_FOUND)

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                borrowing.user = user
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                borrowing.book = book
            except Book.DoesNotExist:
                return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        if expected_return_date:
            borrowing.expected_return_date = expected_return_date

        if status:
            borrowing.status = status


        borrowing.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BorrowingDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, *args, **kwargs):
        """Delete borrowing with the given ID."""
        try:
            borrowing = Borrowing.objects.get(id=pk)
        except Borrowing.DoesNotExist:
            return Response({"error": "Borrowing not found."}, status=status.HTTP_404_NOT_FOUND)

        borrowing.delete()
        return Response({"message": "Borrowing deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ReturnBookView(APIView):
    permission_classes = (IsAdminUser,)

    @extend_schema(
        request=BorrowBookSerializer,
        examples=[
            OpenApiExample(
                "Return book",
                value={"--->": "YOU NEED ONLY ID IN URL"},
                description="""
                To return a book:
    - Send a PATCH request to this endpoint with the `borrowing_id` in the URL (e.g., `/api/borrowing/return/<id>/`).
    - No body data is required in the request.
    
    This action will mark the borrowing as returned and update its status accordingly. 
    The user must be authenticated Admin to perform this action.
                """
            )
        ]
    )

    def patch(self, request, *args, **kwargs):
        user = request.user
        borrowing_id = kwargs.get("pk")
        print(request.data.get("book"), user)

        try:
            borrowing = returned_book(user, borrowing_id)
            return Response(
                {"message": f"Book returned successfully. Status: {borrowing.status}"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
