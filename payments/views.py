from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer


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


class PaymentDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, *args, **kwargs):
        """Delete payment with the given ID."""
        try:
            payment = Payment.objects.get(id=pk)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        payment.delete()
        return Response({"message": "Payment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)