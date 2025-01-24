from django.db import models
from books.models import Book
from library_service.settings import AUTH_USER_MODEL


class Borrowing(models.Model):

    class Status(models.TextChoices):
        BORROWED = "Borrowed", "Borrowed"
        RETURNED = "Returned", "Returned"
        OVERDUE_RETURNED = "Overdue Returned", "Overdue Returned"
        OVERDUE = "Overdue", "Overdue"

    date_borrowed = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(blank=False, null=False)
    actual_return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=17, choices=Status.choices, default=Status.BORROWED)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    overdue_days = models.IntegerField(default=0)


    class Meta:
        ordering = ["expected_return_date"]

    @property
    def duration_day(self):
        """Calculates the number of days for which the book was borrowed."""
        delta = self.expected_return_date - self.date_borrowed
        return abs(delta.days)

    @property
    def overdue_day_count(self):
        """Calculates the number of days overdue."""
        if self.actual_return_date and self.actual_return_date > self.expected_return_date:
            return (self.actual_return_date - self.expected_return_date).days
        return 0

    def calculate_cost(self):
        """Calculates the total cost of the loan, taking into account the penalty for late payment."""
        duration = self.duration_day
        overdue_days = self.overdue_day_count

        cost = duration * self.book.cost_per_day
        if overdue_days > 0:
            overdue_fee = overdue_days * self.book.cost_per_day
            cost += overdue_fee

        return cost

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

    def check_status_pay(self):
        if self.status == self.Status.PAID and self.borrowing.actual_return_date:
            self.borrowing.status = Borrowing.Status.RETURNED

    def save(self, *args, **kwargs):
        """Before saving the payment, we calculate the amount to be paid for the loan."""
        if not self.money_to_pay:
            self.money_to_pay = self.borrowing.calculate_cost()
        super().save(*args, **kwargs)
