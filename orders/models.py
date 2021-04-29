from django.db import models
from accounts.models import Account
from shop.models import Variation,Product


STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled')
    )
class Order(models.Model):
    user = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    order_number = models.CharField(max_length=200)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=500)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    order_note = models.CharField(max_length=300,blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=150,choices=STATUS,default='New')
    ip_address = models.CharField(max_length=100,blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.order_number + " " + self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name