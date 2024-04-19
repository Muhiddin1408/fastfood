import os

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    STATUS = (
        ('admin', "ADMIN"),
        ('user', "USER"),
        ('waiter', "WAITER"),
    )
    status = models.CharField(max_length=123, choices=STATUS)

    def __str__(self):
        return self.username


class Menu(models.Model):
    TYPE = (
        ('food', "FOOD"),
        ('drink', "Drink"),
    )
    type = models.CharField(max_length=123, choices=TYPE)
    name = models.CharField(max_length=123)
    price = models.IntegerField()
    description = models.CharField(max_length=1234)

    def __str__(self):
        return self.name


class ImageMenu(models.Model):
    image = models.ImageField(upload_to='menu/')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)


class Order(models.Model):
    STATUS = (
        ('basket', "BASKET"),
        ('wait', "WAIT"),
        ('sent', "SENT"),
        ('delivered', "DELIVERED"),

    )

    PAYMENT = (
        ('online', 'ONLINE'),
        ('offline', 'OFFLINE'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=123, choices=STATUS)
    payment_status = models.CharField(max_length=123, choices=PAYMENT)
    created_at = models.DateField(auto_created=True, auto_now_add=True)
    delivered_time = models.IntegerField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
    product = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="product_order")
    count = models.IntegerField()
    created_at = models.DateField(auto_created=True, auto_now_add=True)


