from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'groups']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    menuitem_id = serializers.IntegerField(source='menuitem.id')

    class Meta:
        model = Cart
        fields = ['user_id', 'menuitem_id', 'quantity', 'unit_price','price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='id')
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_id = serializers.IntegerField(source='user.id')
    delivery_crew_id = serializers.PrimaryKeyRelatedField(queryset='delivery_set')

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'delivery_crew_id', 'status', \
                  'total', 'date', 'order_items']