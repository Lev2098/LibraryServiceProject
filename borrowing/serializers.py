from rest_framework import serializers

from books.models import Book
from borrowing.models import Borrowing


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BorrowedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = '__all__'