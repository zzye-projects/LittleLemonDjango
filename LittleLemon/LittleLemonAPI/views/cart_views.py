from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import CartSerializer
from ..models import MenuItem, Cart
from ..globals import *
from ..permissions import IsCustomerOr403

class CartView(APIView):
    permission_classes = [IsCustomerOr403]

    def get(self, request):
        cart = Cart.objects.filter(user__username=request.user)\
            .select_related('user', 'menuitem')
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        menuitem = get_object_or_404(MenuItem, pk=request.data.get('menuitem'))
        carts = Cart.objects.filter(user__username=request.user, menuitem=menuitem)

        if not carts:
            cart = Cart.objects.create(
                user=request.user,
                menuitem=menuitem,
                quantity=1,
                unit_price=menuitem.price,
                price=menuitem.price
            )
        else:
            cart = carts[0]
            cart.menuitem=menuitem
            cart.quantity += 1
            cart.price=menuitem.price*cart.quantity

        cart.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        carts = Cart.objects.filter(user__username=request.user)
        carts.delete()
        return Response({'message': 'Cart emptied for user {}'.format(request.user)}, status=status.HTTP_404_NOT_FOUND)