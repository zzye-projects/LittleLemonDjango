from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from LittleLemonAPI.models import Category
from LittleLemonAPI.serializers import CategorySerializer

class CategoryTestCase(APITestCase):
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
        
        self.category1 = Category.objects.create(
            slug = 'category1',
            title = 'Category1'
        )
        self.category2 = Category.objects.create(
            slug = 'category2',
            title = 'Category2'
        )

    def test_list_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = CategorySerializer(Category.objects.all(), many=True)
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = CategorySerializer(self.category1)
        response = self.client.get(reverse('category-detail', kwargs={'pk': self.category1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
    
    def test_post_category(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'slug': 'category3',
            'title': 'Category3'
        }

        response = self.client.post(reverse('category-list'), data=payload)
        serializer = CategorySerializer(get_object_or_404(Category, title='Category3'))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(Category.objects.all()), 3)

    def test_filter_category(self):
        pass

    def test_order_category(self):
        pass

    def test_paginate_category(self):
        pass

    def test_put_category(self):
        pass

    def test_delete_category(self):
        pass

        # self.client.login(username='testuser', password='password')
        # response = self.client.get('/api/secure-endpoint/')
        # self.assertEqual(response.status_code, 200)