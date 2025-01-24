from django.test import TestCase
from django.core.exceptions import ValidationError

from books.models import Book, Author, Genre
from datetime import date


class AuthorModelTest(TestCase):
    def setUp(self):

        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author",
            pseudonym="TestAuthor",
            birth_date=date(1990, 1, 1),
            context="A well-known author."
        )

    def test_author(self):
        self.assertEqual(self.author.first_name, "Test")
        self.assertEqual(self.author.last_name, "Author")
        self.assertEqual(self.author.pseudonym, "TestAuthor")
        self.assertEqual(self.author.birth_date, date(1990, 1, 1))
        self.assertEqual(self.author.context, "A well-known author.")

    def test_author_full_name_pseudonym(self):
        self.assertEqual(self.author.full_name_with_pseudonym, "Test (TestAuthor) Author")

    def test_author_full_name(self):
        self.assertEqual(self.author.full_name, "Test Author")


class GenreModelTest(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(
            name="TestGenre",
        )

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, "TestGenre")


class BookModelTest(TestCase):

    def setUp(self):

        self.author = Author.objects.create(
            first_name="Jane",
            last_name="Smith",
            pseudonym="JS",
            birth_date=date(1990, 1, 1),
            context="ContextTest"
        )

        self.genre = Genre.objects.create(
            name="GenreTest",
        )

        self.book = Book.objects.create(
            title="TestBook",
            publish_date=date(2020, 1, 12),
            context="TestContext",
            author=self.author,
            cover=Book.CoverChoices.HARD,
            count_books_in_library=2,
            cost_per_day=99.01,
        )
        self.book.genre.add(self.genre)

    def test_book_creation(self):

        self.assertEqual(self.book.title, "TestBook")
        self.assertEqual(self.book.publish_date, date(2020, 1, 12))
        self.assertEqual(self.book.context, "TestContext")
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.book.cover, Book.CoverChoices.HARD)
        self.assertEqual(self.book.count_books_in_library, 2)
        self.assertEqual(self.book.cost_per_day, 99.01)
        self.assertEqual(self.book.genre.count(), 1)
        self.assertEqual(self.book.genre.first(), self.genre)

    def test_book_default_cover(self):

        book_with_default_cover = Book.objects.create(
            title="DefaultCoverBookSoft",
            author=self.author,
            count_books_in_library=1
        )
        self.assertEqual(book_with_default_cover.cover, "SOFT")

    def test_book_genre_relationship(self):

        self.assertIn(self.genre, self.book.genre.all())

    def test_invalid_count_books_in_library(self):

        book = Book(
            title="Invalid Book",
            publish_date=date(2020, 1, 12),
            author=self.author,
            cost_per_day=99.00,
            count_books_in_library=-1
        )

        with self.assertRaises(ValidationError) as context:
            book.full_clean()

        error = context.exception

        self.assertIn('count_books_in_library', error.message_dict)

        self.assertEqual(
            error.message_dict['count_books_in_library'],
            ['Ensure this value is greater than or equal to 0.']
        )