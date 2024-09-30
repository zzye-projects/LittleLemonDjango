from django.test import TestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.slug, 'category1')
        self.assertEqual(self.category.title, 'Category1')

class MenuModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        self.menu1 = MenuItem.objects.create(
            title = 'Dish1',
            price = 10.00,
            category = self.category
        )
        self.menu2 = MenuItem.objects.create(
            title = 'Dish2',
            price = 20.00,
            featured = True,
            category = self.category
        )

    def test_menu_creation(self):
        menu1 = get_object_or_404(MenuItem, pk = self.menu1.pk)
        menu2 = get_object_or_404(MenuItem, pk = self.menu2.pk)

        self.assertEqual(MenuItem.objects.count(), 2)

        self.assertEqual(menu1.price, 10.00)
        self.assertEqual(menu1.featured, False)
        self.assertEqual(menu1.category, self.category)

        self.assertEqual(menu2.price, 20.00)
        self.assertEqual(menu2.featured, True)
        self.assertEqual(menu2.category, self.category)

class CartModelTest(TestCase):
    def setUp(self):
        category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        self.menu = MenuItem.objects.create(
            title = 'Dish1',
            price = 11.00,
            category = category
        )
        self.user = User.objects.create(
            username = 'CustomerUser',
            password = 'CustomerUser@123!'
        )
        self.cart = Cart.objects.create(
            user = self.user,
            menuitem = self.menu,
            quantity = 20
        )

    def test_cart_creation(self):
        cart = get_object_or_404(Cart, pk = self.cart.pk)

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.menuitem, self.menu)
        self.assertEqual(cart.quantity, 20)
        self.assertEqual(cart.unit_price, 11.00)
        self.assertEqual(cart.price, 11.00 * 20)

class OrderModelTest(TestCase):
    def setUp(self):
        self.customer_user = User.objects.create(
            username = 'CustomerUser',
            password = 'CustomerUser@123!'
        )
        self.delivery_user = User.objects.create(
            username = 'DeliveryUser',
            password = 'DeliveryUser@123!'
        )
        self.timezone_date = timezone.now().date()
        self.order = Order.objects.create(
            user = self.customer_user,
            delivery_crew = self.delivery_user,
            total = 100.00,
            date = self.timezone_date
        )
    
    def test_order_creation(self):
        order = get_object_or_404(Order, pk = self.order.pk)
        self.assertEqual(order.user, self.customer_user)
        self.assertEqual(order.delivery_crew, self.delivery_user)
        self.assertEqual(order.total, 100.00)
        self.assertEqual(order.date, self.timezone_date)
        self.assertEqual(order.status, 0)

class OrderItemModelTest(TestCase):
    def setUp(self):
        category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        self.menu = MenuItem.objects.create(
            title = 'Dish1',
            price = 10.00,
            category = category
        )
        self.customer_user = User.objects.create(
            username = 'CustomerUser',
            password = 'CustomerUser@123!'
        )
        self.delivery_user = User.objects.create(
            username = 'DeliveryUser',
            password = 'DeliveryUser@123!'
        )
        self.order = Order.objects.create(
            user = self.customer_user,
            delivery_crew = self.delivery_user,
            total = 100.00,
            date = timezone.now().date()
        )
        self.order_item = OrderItem.objects.create(
            order = self.order,
            menuitem = self.menu,
            quantity = 10,
            unit_price = 11.00,
            price = 10 * 11.00
        )

    def test_order_item_creation(self):
        order_item = get_object_or_404(OrderItem, pk=self.order_item.pk)

        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.menuitem, self.menu)
        self.assertEqual(order_item.quantity, 10)
        self.assertEqual(order_item.unit_price, 11.00)
        self.assertEqual(order_item.price, 10 * 11.00)


