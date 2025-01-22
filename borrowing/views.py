from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from borrowing.models import Borrowing, Payment
from borrowing.serializers import (
    BorrowingSerializer,
    PaymentSerializer,
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
        user_id = request.data.get("user")


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


class PaymentCreateView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=PaymentSerializer,
        examples=[
            OpenApiExample(
                "Example Body Payment",
                value={
                    "borrowing": 1,
                    "payment_status": "Paid",
                    "payment_type": "Card",
                    "session_url": None,
                    "session_id": None
                },
                description=" You can add payment borrow use this example !"
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        """Creating a new payment for a loan"""
        borrow_id = request.data.get("borrowing")
        payment_status = request.data.get("payment_status")
        payment_type = request.data.get("payment_type")
        session_url = request.data.get("session_url")
        session_id = request.data.get("session_id")

        try:
            borrow = Borrowing.objects.get(id=borrow_id)
        except Borrowing.DoesNotExist:
            return Response({"error": "Borrow not found."}, status=status.HTTP_404_NOT_FOUND)

        if payment_status not in ["Paid", "Pending"]:
            raise ValidationError("payment_status: must be 'Paid' or 'Pending'")

        if payment_type not in ["Cash", "Card"]:
            raise ValidationError("payment_type must be 'Cash' or 'Card'.")

        payment = Payment.objects.create(
            borrowing=borrow,
            status=payment_status,
            type=payment_type,
            session_url=session_url,
            session_id=session_id,
            money_to_pay=borrow.calculate_cost(),
        )
        payment.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentListAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """Get a list of all users payments"""
        payments = Payment.objects.all()
        payments = payments.order_by(
            "-date_paid"
        )
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentListUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get list user payments"""
        payments = Payment.objects.filter(borrowing__user=request.user)
        payments = payments.order_by(
            "-date_paid"
        )
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details of a specific payment",
    )
    def get(self, request, pk, *args, **kwargs):

        try:
            payment = Payment.objects.get(id=pk)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff and payment.borrowing.user != request.user:
            return Response(
                {"error": "You do not have permission to view this borrowing."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class PaymentUpdateView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request=PaymentSerializer,
        examples=[
            OpenApiExample(
                "Example Body Payment",
                value={
                    "payment_status": "Paid",
                    "payment_type": "Card",
                    "session_url": None,
                    "session_id": None
                },
                description=" You can update payment use this example !"
            )
        ]
    )
    def put(self, request, pk, *args, **kwargs):
        """Update payment (for example, change status to "paid" or type payment to "cash or card")"""

        payment_status = request.data.get("payment_status")
        payment_type = request.data.get("payment_type")
        session_url = request.data.get("session_url")
        session_id = request.data.get("session_id")

        if payment_status not in ["Paid", "Pending"]:
            raise ValidationError("payment_status: must be 'Paid' or 'Pending'")

        if payment_type not in ["Cash", "Card"]:
            raise ValidationError("payment_type must be 'Cash' or 'Card'.")

        with transaction.atomic():
            try:
                payment = Payment.objects.get(id=pk)
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

            payment.status = payment_status
            payment.type = payment_type
            payment.session_url = session_url
            payment.session_id = session_id
            payment.save()

            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)