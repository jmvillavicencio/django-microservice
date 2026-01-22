from django.db import models


class Payment(models.Model):
    """Model to track PayPal payments"""
    
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        APPROVED = 'APPROVED', 'Approved'
        CAPTURED = 'CAPTURED', 'Captured'
        REFUNDED = 'REFUNDED', 'Refunded'
        FAILED = 'FAILED', 'Failed'
    
    paypal_order_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    capture_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.paypal_order_id} - {self.amount} {self.currency}'


class Refund(models.Model):
    """Model to track refunds"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    paypal_refund_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.paypal_refund_id} - {self.amount}'
