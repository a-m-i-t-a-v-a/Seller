# Generated by Django 5.0.1 on 2024-01-20 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_product_total_sales_product_total_sales_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='customer_email',
            field=models.EmailField(max_length=254),
        ),
    ]
