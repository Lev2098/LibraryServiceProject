from django.contrib import admin

from .models import Book, Genre, Author

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(Author)

