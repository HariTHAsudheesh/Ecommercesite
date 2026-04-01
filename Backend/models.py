from django.db import models

# Create your models here.
class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=8,decimal_places=2)
    image=models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name
    
class Order(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # ✅ ADD THESE FIELDS
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {'Paid' if self.is_paid else 'Pending'}"

