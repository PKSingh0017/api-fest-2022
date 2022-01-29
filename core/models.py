from django.db import models
from django.db.models.fields import CharField
from django.utils import timezone
from django.contrib.auth.models import User
from autoslug import AutoSlugField

ORDER_STATUS = {
    ('Created', 'Created'),
    ('Ordered', 'Ordered'),
    ('Ready', 'Ready'),
    ('Dispached', 'Dispached'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
}

TABLE_ORDER_STATUS = {
    ('Created', 'Created'),
    ('Cancelled', 'Cancelled'),
    ('Ready', 'Ready'),
    ('Bill Requested', 'Bill Requested'),
    ('Completed', 'Completed'),
}


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Item(models.Model):
    name = models.CharField(max_length=80, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.FloatField()
    discount_percentage = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='item_pics', default='default.jpg')
    is_nonveg = models.BooleanField()
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField()
    slug = AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return self.name

    def actual_price(self):
        return self.price - (self.price * self.discount_percentage)/100

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    rp_order_id = models.CharField(max_length=20, blank=True, null=True)
    rp_payment_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.get_total_item_price() - (self.quantity * self.item.discount_percentage * self.item.price / 100)

    def get_amount_saved(self):
        return self.quantity * self.item.discount_percentage * self.item.price / 100

    def get_final_price(self):
        if self.item.discount_percentage:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Table(models.Model):
    name = CharField(max_length=50)
    slug = AutoSlugField(populate_from='name', unique=True)
    number_of_seats = models.IntegerField(default=2)
    is_vacent = models.BooleanField(default=True)
    qr_image = models.ImageField(upload_to='TableQRs', default='default_qr.jpg')

    def __str__(self):
        return self.name

class TableOrder(models.Model):
    items = models.ManyToManyField(OrderItem)
    amount = models.IntegerField(default=0)
    table=models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=TABLE_ORDER_STATUS, default='Created')
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.table.name
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total = total + order_item.get_final_price()
        return total

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rp_order_id = models.CharField(max_length=20, blank=True, null=True)
    rp_payment_id = models.CharField(max_length=20, blank=True, null=True)

    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True)
    ordered = models.BooleanField(default=False)
    address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    cash_on_delivery = models.BooleanField(default=False)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    delivery_charge = models.IntegerField(default=0)

    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Created')

    def __str__(self):
        return self.user.username

    def is_payment_pending(self):
        if self.rp_order_id:
            if self.rp_payment_id:
                return False
            else:
                return True
        else:
            False

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total = total + order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    
    def get_total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

class SellerSale(models.Model):
    items = models.ManyToManyField(OrderItem)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.seller.user.username

    def get_sellers_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

class Address(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    # city = models.CharField(max_length=100)
    # district = models.CharField(max_length=100)
    # state = models.CharField(max_length=100)
    # country = CountryField(multiple=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    zip = models.CharField(max_length=100)
    # default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    rp_payment_id = models.CharField(max_length=20, blank=True, null=True)
    rp_order_id = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class DefaultAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class MetaData(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

