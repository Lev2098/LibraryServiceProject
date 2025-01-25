# Generated by Django 5.1.4 on 2025-01-23 13:10

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("pseudonym", models.CharField(max_length=255, null=True)),
                ("birth_date", models.DateField(null=True)),
                ("context", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("publish_date", models.DateField(null=True)),
                ("context", models.TextField(blank=True, null=True)),
                (
                    "cover",
                    models.CharField(
                        choices=[("HARD", "Hardcover"), ("SOFT", "Softcover")],
                        default="SOFT",
                        max_length=10,
                    ),
                ),
                (
                    "count_books_in_library",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "cost_per_day",
                    models.DecimalField(decimal_places=2, max_digits=6, null=True),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="books.author",
                    ),
                ),
                (
                    "genre",
                    models.ManyToManyField(
                        blank=True, related_name="books", to="books.genre"
                    ),
                ),
            ],
        ),
    ]
