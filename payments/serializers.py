from rest_framework import serializers

from borrowing.models import Borrowing
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(queryset=Borrowing.objects.all())

    class Meta:
        model = Payment
        fields = ["id", "status", "type", "date_paid", "money_to_pay", "session_url", "session_id", "borrowing"]
        read_only_fields = ["money_to_pay"]

    def create(self, validated_data):
        """Створюємо новий платіж."""
        return Payment.objects.create(**validated_data)

