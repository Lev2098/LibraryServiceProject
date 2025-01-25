from django.db import models

from borrowing.models import Borrowing


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
