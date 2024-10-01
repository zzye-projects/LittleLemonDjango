from rest_framework.test import APITestCase
from LittleLemonAPI.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from LittleLemonAPI.serializers import UserSerializer

class UserTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        cls.delivery_user = User.objects.create_user(
            username='DeliveryUser', 
            password='DeliveryUser@123!'
        )
        group, created = Group.objects.get_or_create(name='Delivery Crew')
        cls.delivery_user.groups.add(group)

        cls.manager_user = User.objects.create_user(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        group, created = Group.objects.get_or_create(name='Manager')
        cls.manager_user.groups.add(group)

        cls.customer_user = User.objects.create_user(
            username='CustomerUser', 
            password='CustomerUser@123!'
        )

    def test_auth_list_user(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('group-list', kwargs={'role':'manager'}))
        self.assertEqual(response.status_code, 403)

    def test_list_manager_user(self):
        self.client.login(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        response = self.client.get(reverse('group-list', kwargs={'role':'manager'}))
        serializer = UserSerializer(self.manager_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], serializer.data)

    def test_list_delivery_user(self):
        self.client.login(
            username='ManagerUser', 
            password='ManagerUser@123!'
        )
        response = self.client.get(reverse('group-list', kwargs={'role':'delivery-crew'}))
        serializer = UserSerializer(self.delivery_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], serializer.data)

    def test_add_manager_user(self):
        self.client.login(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        payload = {
            'username': self.customer_user.username
        }
        response = self.client.post(
            reverse('group-list', kwargs={'role':'manager'}), data=payload, format='json')
        user = get_object_or_404(User, pk=self.customer_user.pk)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.groups.filter(name='Manager').exists(), True)

    def test_remove_manager_user(self):
        self.client.login(
            username='SuperUser', 
            password='SuperUser@123!'
        )
        response = self.client.delete(
            reverse('group-detail', kwargs={'role':'manager', 'pk': self.manager_user.pk}))
        user = get_object_or_404(User, pk=self.manager_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.groups.filter(name='Manager').exists(), False)