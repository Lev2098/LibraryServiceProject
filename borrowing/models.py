from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_init
from datetime import date
from books.models import Book
from library_service.settings import AUTH_USER_MODEL


class Borrowing(models.Model):
    class Status(models.TextChoices):
        BORROWED = "Borrowed", "Borrowed"
        RETURNED = "Returned", "Returned"
        OVERDUE = "Overdue", "Overdue"

    date_borrowed = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(blank=False, null=False)
    actual_return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BORROWED)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    overdue_days = models.IntegerField(default=0)

    @property
    def duration_day(self):
        return (self.expected_return_date - self.date_borrowed).days

    def calculate_overdue_days(self):
        today = date.today()
        if today > self.expected_return_date.date():
            self.overdue_days = (today - self.expected_return_date.date()).days
        else:
            self.overdue_days = 0

    def save(self, *args, **kwargs):
        today = date.today()
        if today > self.expected_return_date.date():
            self.overdue_days = (today - self.expected_return_date.date()).days
        else:
            self.overdue_days = 0
        super().save(*args, **kwargs)


@receiver(post_init, sender=Borrowing)
def update_overdue_days(sender, instance, **kwargs):
    instance.calculate_overdue_days()


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        PAID = "Paid", "Paid"

    class Type(models.TextChoices):
        CASH = "Cash", "Cash"
        CARD = "Card", "Card"

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.CASH)
    date_paid = models.DateTimeField(auto_now_add=True)
    money_to_pay = models.IntegerField(blank=False, null=False)
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)

    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment for Borrowing {self.borrowing.id} - {self.status}"