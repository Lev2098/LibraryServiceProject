from django.urls import path, include
from rest_framework import routers

from .views import (
    BooksViewSet,
    GenresViewSet,
    AuthorsViewSet
)

app_name = "books"

router = routers.DefaultRouter()

router.register("books", BooksViewSet, basename="books")
router.register("genres", GenresViewSet, basename="genres")
router.register("authors", AuthorsViewSet, basename="authors")

urlpatterns = [
    path("", include(router.urls)),

]