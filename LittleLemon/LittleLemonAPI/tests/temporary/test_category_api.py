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
    
    def test_auth_list_category(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, 401)

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
    
    def test_auth_post_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        payload = {
            'slug': 'category3',
            'title': 'Category3'
        }
        response = self.client.post(
            reverse('category-list'), 
            data=payload, 
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_post_category(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'slug': 'category3',
            'title': 'Category3'
        }

        response = self.client.post(
            reverse('category-list'), 
            data=payload, 
            format='json'
        )
        category = get_object_or_404(Category, title='Category3')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(category.slug, 'category3')
        self.assertEqual(category.title, 'Category3')
        self.assertEqual(len(Category.objects.all()), 3)

    def test_filter_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = CategorySerializer(self.category1)
        response = self.client.get(reverse('category-list'), {'title__icontains':'1'})
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_order_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )
        
        serializer1 = CategorySerializer(self.category1)
        serializer2 = CategorySerializer(self.category2)

        response = self.client.get(reverse('category-list'), {'ordering':'-slug'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0], serializer2.data)
        self.assertEqual(response.data['results'][1], serializer1.data)

    def test_paginate_category(self):
        self.client.login(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

        serializer = CategorySerializer(self.category2)
        response = self.client.get(reverse('category-list'), {'page_size':'1', 'page': 2})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], serializer.data)

    def test_put_category(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'slug' : 'category11',
            'title' : 'Category11'
        }
        response = self.client.put(
            reverse('category-detail',
            kwargs={'pk': self.category1.pk}), 
            data=payload, format='json'
        )
        category = get_object_or_404(Category, pk=self.category1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(category.title, 'Category11')
        self.assertEqual(category.slug, 'category11')
        self.assertEqual(len(Category.objects.all()), 2)

    def test_patch_category(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        payload = {
            'slug' : 'category11',
        }
        response = self.client.patch(
            reverse('category-detail',
            kwargs={'pk': self.category1.pk}), 
            data=payload, format='json'
        )
        category = get_object_or_404(Category, pk=self.category1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(category.title, 'Category1')
        self.assertEqual(category.slug, 'category11')
        self.assertEqual(len(Category.objects.all()), 2)

    def test_delete_category(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.delete(
            reverse('category-detail',
            kwargs={'pk': self.category1.pk})
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Category.objects.all()), 1)
        self.assertEqual(len(Category.objects.filter(pk=self.category1.pk)), 0)