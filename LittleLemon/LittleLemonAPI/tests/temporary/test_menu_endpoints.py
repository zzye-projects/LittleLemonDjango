from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer

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
        self.manager_user = User.objects.create_user(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        group, created = Group.objects.get_or_create(name='Manager')
        self.manager_user.groups.add(group)
        
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
    
    def test_auth_list_menu(self):
        response = self.client.get(reverse('menuitem-list'))
        self.assertEqual(response.status_code, 401)

    def test_list_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(MenuItem.objects.all(), many=True)
        response = self.client.get(reverse('menuitem-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu1)
        response = self.client.get(reverse('menuitem-detail', kwargs={'pk': self.menu1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
    
    def test_auth_post_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        payload = {
            'title' : 'Dish3',
            'price' : 30.00,
            'featured' : True,
            'category_id' : self.category.id
        }
        response = self.client.post(
            reverse('menuitem-list'), 
            data=payload, 
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_post_menu(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'title' : 'Dish3',
            'price' : 30.00,
            'featured' : True,
            'category_id' : self.category.id
        }
        response = self.client.post(
            reverse('menuitem-list'), 
            data=payload, 
            format='json'
        )
        menu = get_object_or_404(MenuItem, title='Dish3')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(menu.price, 30.00)
        self.assertEqual(menu.featured, True)
        self.assertEqual(menu.category, self.category)
        self.assertEqual(len(MenuItem.objects.all()), 3)

    def test_filter_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu1)
        response = self.client.get(reverse('menuitem-list'), {'price__lte': 10.00})
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_order_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        
        serializer1 = MenuItemSerializer(self.menu1)
        serializer2 = MenuItemSerializer(self.menu2)

        response = self.client.get(reverse('menuitem-list'), {'ordering':'-title'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0], serializer2.data)
        self.assertEqual(response.data['results'][1], serializer1.data)

    def test_paginate_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu2)
        response = self.client.get(reverse('menuitem-list'), {'page_size':'1', 'page': 2})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_put_menu(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'title' : 'Dish11',
            'price' : 11.00,
            'featured' : False,
            'category_id' : self.category.id
        }
        response = self.client.put(
            reverse('menuitem-detail',
            kwargs={'pk': self.menu1.pk}), 
            data=payload, format='json'
        )
        menu = get_object_or_404(MenuItem, pk=self.menu1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(menu.title, 'Dish11')
        self.assertEqual(menu.price, 11.00)
        self.assertEqual(menu.featured, False)
        self.assertEqual(menu.category, self.category)
        self.assertEqual(len(MenuItem.objects.all()), 2)

    def test_delete_menu(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.delete(
            reverse('menuitem-detail',
            kwargs={'pk': self.menu1.pk})
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(MenuItem.objects.all()), 1)
        self.assertEqual(len(MenuItem.objects.filter(pk=self.menu1.pk)), 0)