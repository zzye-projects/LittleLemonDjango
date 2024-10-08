from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from LittleLemonAPI.models import Order, OrderItem
from LittleLemonAPI.serializers import OrderSerializer
from datetime import timedelta
from django.utils import timezone

class OrderTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup Users
        cls.customer1 = User.objects.create_user(
            username='Customer1', 
            password='Customer1@123!'
        )
        cls.customer2 = User.objects.create_user(
            username='Customer2', 
            password='Customer2@123!'
        )
        cls.manager_user = User.objects.create_user(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        manager_group, created = Group.objects.get_or_create(name='Manager')
        cls.manager_user.groups.add(manager_group)
        
        cls.delivery_user = User.objects.create_user(
            username='DeliveryUser', 
            password='DeliveryUser@123!'
        )
        delivery_group, created = Group.objects.get_or_create(name='Delivery Crew')
        cls.delivery_user.groups.add(delivery_group)

        # Setup category and menu items
        cls.category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        cls.menu1 = MenuItem.objects.create(
            title = 'Dish1',
            price = 11.00,
            category = cls.category
        )
        cls.menu2 = MenuItem.objects.create(
            title = 'Dish2',
            price = 22.00,
            category = cls.category
        )
        cls.menu3 = MenuItem.objects.create(
            title = 'Dish3',
            price = 33.00,
            category = cls.category
        )
        # Setup cart and orders for customer1
        cls.timezone_date = timezone.now().date()
        cls.order1 = Order.objects.create(
            user = cls.customer1,
            total = 10 * 11.00,
            date = timezone.now().date() + timedelta(days=1)
        )
        cls.order_item1 = OrderItem.objects.create(
            order = cls.order1,
            menuitem = cls.menu1,
            quantity = 10,
            unit_price = 11.00,
            price = 10 * 11.00
        )
        cls.cart1_menu2 = Cart.objects.create(
            user = cls.customer1,
            menuitem = cls.menu2,
            quantity = 20
        )
        cls.cart1_menu3 = Cart.objects.create(
            user = cls.customer1,
            menuitem = cls.menu3,
            quantity = 30
        )
        # Setup cart and orders for customer2
        cls.order2 = Order.objects.create(
            user = cls.customer2,
            delivery_crew = cls.delivery_user,
            total = 20 * 22.00,
            date = timezone.now().date() + timedelta(days=2)
        )
        cls.order_item2 = OrderItem.objects.create(
            order = cls.order2,
            menuitem = cls.menu2,
            quantity = 20,
            unit_price = 22.00,
            price = 20 * 22.00
        )
        
    def test_auth_list_order(self):
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 401)

    def test_customer_list_order(self):
        self.client.login(
            username='Customer1', 
            password='Customer1@123!'
        )
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)
    
    def test_manager_list_order(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 200)

        serializer1 = OrderSerializer(self.order1)
        serializer2 = OrderSerializer(self.order2)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0], serializer1.data)
        self.assertEqual(response.data['results'][1], serializer2.data)

    def test_delivery_list_order(self):
        self.client.login(
            username='DeliveryUser', 
            password='DeliveryUser@123!'
        )
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order2)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_filter_order_by_delivery(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-list'), 
                                   {'delivery_crew__id':self.delivery_user.pk})
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order2)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_filter_order_by_date(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-list'), 
                                   {'date__gte': self.timezone_date + timedelta(days=3) })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_sort_order_by_user(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-list'), 
                                   {'ordering':'-user__id'})
        self.assertEqual(response.status_code, 200)

        serializer1 = OrderSerializer(self.order1)
        serializer2 = OrderSerializer(self.order2)

        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0], serializer2.data)
        self.assertEqual(response.data['results'][1], serializer1.data)

    def test_pagination_order(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-list'), 
                                   {'page_size':1, 'page':2})
        self.assertEqual(response.status_code, 200)

        serializer2 = OrderSerializer(self.order2)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer2.data)

    def test_post_empty_cart(self):
        self.client.login(
            username='Customer2', 
            password='Customer2@123!'
        )
        response = self.client.post(reverse('order-list'))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Order.objects.filter(user__id = self.customer2.id)), 1)

    def test_post_one_cart(self):
        self.client.login(
            username='Customer1', 
            password='Customer1@123!'
        )
        response = self.client.post(reverse('order-list'))
        self.assertEqual(response.status_code, 200)

        order = get_object_or_404(Order, id = self.order1.id)
        self.assertEqual(order.total, 10 * 11.00 + 20 * 22.00 + 30 * 33.00)
        self.assertEqual(len(OrderItem.objects.filter(order=order)), 3)
        
        order_item2 = get_object_or_404(
            OrderItem,
            order = order,
            menuitem = self.menu2
        )
        self.assertEqual(order_item2.quantity, 20)
        self.assertEqual(order_item2.price, 20 * 22.00)

        order_item3 = get_object_or_404(
            OrderItem,
            order = order,
            menuitem = self.menu3
        )
        self.assertEqual(order_item3.quantity, 30)
        self.assertEqual(order_item3.price, 30 * 33.00)

        self.assertEqual(len(Cart.objects.filter(user=self.customer1)), 0)

    def test_customer_get_order(self):
        self.client.login(
            username='Customer1', 
            password='Customer1@123!'
        )
        response = self.client.get(reverse('order-detail', kwargs={'pk':self.order1.pk}))
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order1)
        self.assertEqual(response.data, serializer.data)
        
    def test_manager_get_order(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('order-detail', kwargs={'pk':self.order2.pk}))
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order2)
        self.assertEqual(response.data, serializer.data)

    def test_delivery_get_order(self):
        self.client.login(
            username='DeliveryUser', 
            password='DeliveryUser@123!'
        )

        response = self.client.get(reverse('order-detail', kwargs={'pk': self.order2.pk}))
        self.assertEqual(response.status_code, 200)

        serializer = OrderSerializer(self.order2)
        self.assertEqual(response.data, serializer.data)
    
    def test_delete_order(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.delete(reverse('order-detail', kwargs={'pk':self.order2.pk}))
        self.assertEqual(response.status_code, 204)

        self.assertEqual(len(Order.objects.all()), 1)
        self.assertEqual(len(Order.objects.filter(user=self.customer2)), 0)
        self.assertEqual(len(OrderItem.objects.filter(order=self.order2)), 0)
    
    def test_put_order(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        new_date = self.order1.date + timedelta(days=3)
        payload = {
            'delivery_crew_id': self.delivery_user.pk,
            'status': 1,
            'date': new_date        
        }
        response = self.client.put(reverse('order-detail', kwargs={'pk': self.order1.pk}), 
                                      data=payload, format='json')
        updated_order = get_object_or_404(Order, pk = self.order1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_order.delivery_crew, self.delivery_user)
        self.assertEqual(updated_order.status, 1)
        self.assertEqual(updated_order.date, new_date)

    def test_patch_order(self):
        self.client.login(
            username='DeliveryUser', 
            password='DeliveryUser@123!'
        )
        payload = {
            'status': 1,
        }
        response = self.client.patch(reverse('order-detail', kwargs={'pk': self.order2.pk}), 
                                      data=payload, format='json')
        updated_order = get_object_or_404(Order, pk = self.order2.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_order.delivery_crew, self.delivery_user)
        self.assertEqual(updated_order.status, 1)
        self.assertEqual(updated_order.date, self.timezone_date + timedelta(days=2))





