from django.test import TestCase
from datetime import date, timedelta

from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowing.models import Borrowing
from borrowing.services import borrow_book, returned_book
from user.models import User


class BorrowingTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test_user@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            cost_per_day=10.00,
            count_books_in_library=5,
        )
        self.expected_return_date = date.today() + timedelta(days=7)

    def test_borrow_book_success(self):

        borrowing = borrow_book(
            user=self.user,
            book_id=self.book.id,
            expected_return_date=self.expected_return_date,
        )

        self.book.refresh_from_db()
        self.assertEqual(self.book.count_books_in_library, 4)

        self.assertIsInstance(borrowing, Borrowing)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.expected_return_date, self.expected_return_date)
        self.assertEqual(borrowing.status, Borrowing.Status.BORROWED)

    def test_borrow_book_unavailable(self):
        self.book.count_books_in_library = 0
        self.book.save()

        with self.assertRaises(ValidationError) as context:
            borrow_book(
                user=self.user,
                book_id=self.book.id,
                expected_return_date=self.expected_return_date,
            )

        self.assertEqual(
            str(context.exception),
            "[ErrorDetail(string='The book is not available for borrowing.', code='invalid')]",
        )

    def test_return_book_success(self):

        borrowing = borrow_book(
            user=self.user,
            book_id=self.book.id,
            expected_return_date=self.expected_return_date,
        )

        returned_borrowing = returned_book(
            user=self.user,
            borrowing_id=borrowing.id,
        )

        self.assertEqual(returned_borrowing.status, Borrowing.Status.RETURNED)
        self.assertEqual(returned_borrowing.actual_return_date, date.today())

        self.book.refresh_from_db()
        self.assertEqual(self.book.count_books_in_library, 5)

    def test_return_book_with_overdue(self):

        overdue_borrowing = borrow_book(
            user=self.user,
            book_id=self.book.id,
            expected_return_date=date.today() - timedelta(days=3),  # Прострочена дата
        )

        returned_borrowing = returned_book(
            user=self.user,
            borrowing_id=overdue_borrowing.id,
        )

        self.assertEqual(returned_borrowing.status, Borrowing.Status.OVERDUE_RETURNED)
        self.assertEqual(returned_borrowing.actual_return_date, date.today())

    def test_return_book_already_returned(self):

        borrowing = borrow_book(
            user=self.user,
            book_id=self.book.id,
            expected_return_date=self.expected_return_date,
        )
        returned_book(user=self.user, borrowing_id=borrowing.id)

        with self.assertRaises(ValidationError) as context:
            returned_book(user=self.user, borrowing_id=borrowing.id)

        self.assertEqual(
            str(context.exception), "[ErrorDetail(string='This book has already been returned.', code='invalid')]"
        )

    def test_return_book_not_borrowed(self):

        with self.assertRaises(ValidationError) as context:
            returned_book(user=self.user, borrowing_id=999)

        self.assertEqual(
            str(context.exception), "[ErrorDetail(string='Borrow with this ID was not found.', code='invalid')]"
        )