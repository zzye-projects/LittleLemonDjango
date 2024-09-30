from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from LittleLemonAPI.models import Cart
from LittleLemonAPI.serializers import CartSerializer

class MenuTestCase(APITestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        self.customer_user = User.objects.create_user(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        self.category = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        self.menu1 = MenuItem.objects.create(
            title = 'Dish1',
            price = 11.00,
            category = self.category
        )
        self.menu2 = MenuItem.objects.create(
            title = 'Dish2',
            price = 22.00,
            category = self.category
        )
        self.cart1 = Cart.objects.create(
            user = self.customer_user,
            menuitem = self.menu1,
            quantity = 10
        )
        
    def test_auth_list_cart(self):
        self.client.login(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 403)

    def test_list_cart(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = CartSerializer(Cart.objects.filter(user__id=self.customer_user.id),
                                    many=True)
        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_post_cart(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        payload1 = { 'menuitem_id': self.menu1.id }
        payload2 = { 'menuitem_id': self.menu2.id }

        response = self.client.post(reverse('cart'), payload1, format = 'json')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('cart'), payload2, format = 'json')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('cart'), payload2, format = 'json')
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(Cart.objects.filter(user__id=self.customer_user.id)), 2)

        cart1 = get_object_or_404(Cart, 
                                  user__id=self.customer_user.id, menuitem=self.menu1.id)
        self.assertEqual(cart1.quantity, 11)
        self.assertEqual(cart1.unit_price, 11.00)
        self.assertEqual(cart1.price, 11 * 11.00)

        cart2 = get_object_or_404(Cart, 
                                  user__id=self.customer_user.id, menuitem=self.menu2.id)
        self.assertEqual(cart2.quantity, 2)
        self.assertEqual(cart2.unit_price, 22.00)
        self.assertEqual(cart2.price, 2 * 22.00)

    def test_delete_cart(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        response = self.client.delete(reverse('cart'))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(Cart.objects.filter(user__id=self.customer_user.id)), 0)