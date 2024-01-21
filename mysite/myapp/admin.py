from django.contrib import admin
from .models import Product,OrderDetail
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=('name','description','price')
    list_filter=('name','price')
    
class OrderDetailAdmin(admin.ModelAdmin):
    list_display=('customer_email','product','amount')
    
admin.site.register(Product,ProductAdmin)
admin.site.register(OrderDetail)