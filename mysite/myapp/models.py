from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    seller=models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    name=models.CharField(max_length=150)
    description=models.CharField(max_length=200)
    price=models.FloatField()
    file=models.FileField(upload_to="uploads")
    total_sales_amount=models.FloatField(default=0)
    total_sales=models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.name} {self.price}'
    
class OrderDetail(models.Model):
    customer_email=models.EmailField()
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    amount=models.IntegerField()
    stripe_payment_intent=models.CharField(max_length=200, blank=True, null=True)
    has_paid=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.customer_email} {self.product} {self.amount}'