from rest_framework import serializers

from books.models import Book
from user.models import User
from borrowing.models import Borrowing


class BorrowBookSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID user, this user take book")
    book_id = serializers.IntegerField(help_text="ID borrowed book")
    expected_return_date = serializers.DateField(help_text="Expected return date")


class BorrowingSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    cost_book_per_one_day = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    duration_day = serializers.ReadOnlyField()
    overdue_day_count = serializers.ReadOnlyField()
    cost = serializers.ReadOnlyField(source="calculate_cost")

    class Meta:
        model = Borrowing
        fields = ["id",
                  "user",
                  "book",
                  "date_borrowed",
                  "expected_return_date",
                  "actual_return_date",
                  "status",
                   "cost_book_per_one_day",
                  "duration_day", "overdue_day_count", "cost"]
        read_only_fields = ["date_borrowed", "overdue_days"]

    def get_cost_book_per_one_day(self, obj):
        """Метод для отримання ціни за один день із пов’язаної моделі книги."""
        return obj.book.cost_per_day
