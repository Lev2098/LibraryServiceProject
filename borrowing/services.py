from datetime import date

from django.db import transaction, IntegrityError
from django.db.models.functions import NullIf
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from books.models import Book
from .models import Borrowing, Payment


def borrow_book(user, book_id, expected_return_date):
    """
    Function for borrowing books.
    Changes the inventory of a book, creates a Borrowing record, and ensures that the book is available.
    """
    try:
        with transaction.atomic():
            book = Book.objects.get(id=book_id)
            print(user, expected_return_date, book)

            if book.count_books_in_library <= 0:
                raise ValidationError("The book is not available for borrowing.")

            book.count_books_in_library -= 1
            book.save()

            borrowing = Borrowing.objects.create(
                user=user,
                book=book,
                date_borrowed=date.today(),
                expected_return_date=expected_return_date,
                status=Borrowing.Status.BORROWED,
            )

        return borrowing

    except Book.DoesNotExist:
        raise ValidationError("The book with this ID was not found.")
    except IntegrityError as e:
        raise ValidationError(e)


def returned_book(user, borrowing_id):
    """
    Book return function.
    Increases the book inventory and updates the Borrowing record with statuses:
    - RETURNED: if the book is returned on time.
    - RETURNED_OVERDUE: if the book is returned late.
    - OVERDUE: if the book is still not returned after the expected return date.
    """

    try:
        with transaction.atomic():
            borrowing = Borrowing.objects.get(
                id=borrowing_id
            )
            book = borrowing.book
            if not borrowing:
                raise ValidationError("No active loan record found for this book.")
            if borrowing.actual_return_date:
                raise ValidationError("This book has already been returned.")

            borrowing.actual_return_date = date.today()

            if borrowing.actual_return_date > borrowing.expected_return_date:
                borrowing.status = Borrowing.Status.OVERDUE_RETURNED
            else:
                borrowing.status = Borrowing.Status.RETURNED

            book.count_books_in_library += 1
            book.save()

            borrowing.save()

        return borrowing

    except Book.DoesNotExist:
        raise ValidationError("This book with this ID was not found.")
    except Borrowing.DoesNotExist:
        raise ValidationError("Borrow with this ID was not found.")
    except IntegrityError:
        raise ValidationError("An error occurred while returning the book.")
