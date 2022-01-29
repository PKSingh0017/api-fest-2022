from rest_framework import serializers
from .models import Item, Category, Address, Order, OrderItem, Table, TableOrder
from django.contrib.auth.models import User


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('image',)
        model = Item

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Table

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Category

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Address

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('password', )
        model = User

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    class Meta:
        fields = '__all__'
        model = OrderItem

class TableOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        fields = '__all__'
        model = TableOrder

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Order
