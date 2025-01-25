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
