from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from books.models import Book, Genre, Author
from .serializers import (
    BookSerializer,
    GenreSerializer,
    AuthorSerializer
)


class BooksViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()


class GenresViewSet(ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class AuthorsViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()