from django.db import models


class Book(models.Model):
    
    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hardcover"
        SOFT = "SOFT", "Softcover"
        
    title = models.CharField(max_length=255, null=False)
    publish_date = models.DateField(null=True)
    context = models.TextField(null=True)
    author = models.ForeignKey("Author", on_delete=models.DO_NOTHING, null=True)
    genre = models.ManyToManyField("Genre", null=True)
    cover = models.CharField(
        max_length=10,
        choices=CoverChoices.choices,
        default=CoverChoices.SOFT,
    )


class Genre(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    pseudonym = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    context = models.TextField(null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_with_pseudonym(self):
        return f"{self.first_name} ({self.pseudonym}) {self.last_name}"