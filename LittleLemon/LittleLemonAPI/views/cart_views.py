from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import CartSerializer
from ..models import MenuItem, Cart
from ..permissions import IsCustomerOr403

class CartView(APIView):
    permission_classes = [IsCustomerOr403]

    def get(self, request):
        cart = Cart.objects.filter(user__username=request.user)\
            .select_related('user', 'menuitem')
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        menuitem_id, quantity, cart = request.data.get('menuitem_id'), 1, None
        menuitem = get_object_or_404(MenuItem, pk=menuitem_id)
        carts = Cart.objects.filter(user__username=request.user, menuitem=menuitem)
        
        if len(carts):
            cart = carts[0]
            quantity += cart.quantity
            
        serializer = CartSerializer(cart, data = {
            'user_id': request.user.id,
            'menuitem_id': menuitem_id,
            'quantity' : quantity
        })

        if serializer.is_valid(): serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        carts = Cart.objects.filter(user__username=request.user)
        carts.delete()
        return Response({'message': f'Cart emptied for user {request.user}'}, 
                        status=status.HTTP_404_NOT_FOUND)