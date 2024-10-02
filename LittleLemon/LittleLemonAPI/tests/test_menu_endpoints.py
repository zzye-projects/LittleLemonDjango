from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer

class MenuTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        cls.customer_user = User.objects.create_user(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        cls.manager_user = User.objects.create_user(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        group, created = Group.objects.get_or_create(name='Manager')
        cls.manager_user.groups.add(group)
        
        cls.category1 = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        cls.category2 = Category.objects.create(
            slug = 'category2',
            title = 'Category2'
        )
        cls.menu1 = MenuItem.objects.create(
            title = 'Dish1',
            price = 10.00,
            category = cls.category1
        )
        cls.menu2 = MenuItem.objects.create(
            title = 'Dish2',
            price = 20.00,
            featured = True,
            category = cls.category2
        )
    
    def test_auth_list_menu(self):
        response = self.client.get(reverse('menu-list'))
        self.assertEqual(response.status_code, 401)

    def test_list_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(MenuItem.objects.all(), many=True)
        response = self.client.get(reverse('menu-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu1)
        response = self.client.get(reverse('menu-detail', kwargs={'pk': self.menu1.pk}))
        
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
            'category_id' : self.category1.id
        }
        response = self.client.post(
            reverse('menu-list'), 
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
            'category_id' : self.category1.id
        }
        response = self.client.post(
            reverse('menu-list'), 
            data=payload, 
            format='json'
        )
        menu = get_object_or_404(MenuItem, title='Dish3')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(menu.price, 30.00)
        self.assertEqual(menu.featured, True)
        self.assertEqual(menu.category, self.category1)
        self.assertEqual(len(MenuItem.objects.all()), 3)

    def test_filter_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu1)
        response = self.client.get(reverse('menu-list'), {'price__lte': 10.00})
        
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

        response = self.client.get(reverse('menu-list'), {'ordering':'-title'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0], serializer2.data)
        self.assertEqual(response.data['results'][1], serializer1.data)

    def test_paginate_menu(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = MenuItemSerializer(self.menu2)
        response = self.client.get(reverse('menu-list'), {'page_size':'1', 'page': 2})
        
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
            'category_id' : self.category2.id
        }
        response = self.client.put(
            reverse('menu-detail',
            kwargs={'pk': self.menu1.pk}), 
            data=payload, format='json'
        )
        menu = get_object_or_404(MenuItem, pk=self.menu1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(menu.title, 'Dish11')
        self.assertEqual(menu.price, 11.00)
        self.assertEqual(menu.featured, False)
        self.assertEqual(menu.category, self.category2)
        self.assertEqual(len(MenuItem.objects.all()), 2)

    def test_patch_menu(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'title' : 'Dish12',
        }
        response = self.client.patch(
            reverse('menu-detail',
            kwargs={'pk': self.menu1.pk}), 
            data=payload, format='json'
        )
        menu = get_object_or_404(MenuItem, pk=self.menu1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(menu.title, 'Dish12')
        self.assertEqual(menu.price, 10.00)
        self.assertEqual(menu.featured, False)
        self.assertEqual(menu.category, self.category1)
        self.assertEqual(len(MenuItem.objects.all()), 2)

    def test_delete_menu(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.delete(
            reverse('menu-detail',
            kwargs={'pk': self.menu1.pk})
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(MenuItem.objects.all()), 1)
        self.assertEqual(len(MenuItem.objects.filter(pk=self.menu1.pk)), 0)