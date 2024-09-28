from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..serializers import OrderSerializer
from ..models import Cart, Order, OrderItem
from ..permissions import IsCustomerOrGET, SingleOrderPermissions
from rest_framework.exceptions import ValidationError
from ..helpers import get_filtered_items, get_paginated_items
from django.core.paginator import EmptyPage
    
def get_role_orders(user):
    user_groups = user.groups.all()
    if not user_groups: # Customer
        return Order.objects.filter(user=user)
    elif user_groups.filter(id='Manager'): # Manager
        return Order.objects.all()
    elif user_groups.filter(id='Delivery-crew'): # Delivery-crew
        return Order.objects.filter(delivery_crew=user)
    else:
        return None
        
def update_status(order, status_code):
    if status_code in (0, 1): 
        order.status=status_code
        order.save()
    else:
        raise ValidationError('Invalid status code')   
     
def update_delivery_crew(order, delivery_crew_id):
    delivery_crew = User.objects \
        .filter(pk=delivery_crew_id, groups__id='Delivery-crew') \
        .first()
    if delivery_crew_id and not delivery_crew:
        raise ValidationError('Invalid user id for the delivery crew')
    elif delivery_crew_id: order.delivery_crew=delivery_crew
    order.save()

class OrderView(APIView):
    permission_classes = [IsCustomerOrGET]

    def get(self, request):
        order = get_role_orders(request.user)    

        # Filter orders
        filter_params = {'user_id': 'user__id', 
                    'delivery_crew': 'delivery_crew__id',
                    'status' : 'status', 
                    'to_total': 'total__lte', 
                    'to_date':'date__lte',
                    }
        order = get_filtered_items(order, request, filter_params)

        if order:
            # Order menu-items
            order_params = request.query_params.get('ordering')
            if order_params: order = order.order_by(*order_params.split(','))

            # Apply pagination
            try:
                order = get_paginated_items(order, request)
            except EmptyPage:
                return Response({'message':'Invalid page'}, status=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message':'No orders found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        if not carts.first(): 
            return Response({'message': 'Your cart is empty. No orders to be submitted'}, \
                            status=status.HTTP_204_NO_CONTENT)
        
        order = Order.objects.create(user=user)
        for cart in carts:
            order_item = OrderItem.objects.create(
                order = order,
                menuitem = cart.menuitem,
                quantity = cart.quantity,
                unit_price = cart.unit_price,
                price = cart.price
            )
            order_item.save()
            cart.delete()
            order.total += order_item.price
            order.save()

        return Response({'message': 'Cart items (total: {}) added to order for user {}'.\
                         format(order.total, user)}, status=status.HTTP_200_OK)
        
class SingleOrderView(APIView):
    permission_classes = [SingleOrderPermissions]

    def get(self, request, pk):
        order = get_role_orders(request.user).filter(pk=pk) 
        if order:
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'Order not found'.format(request.user)}, \
                            status=status.HTTP_404_NOT_FOUND) 
        
    def put(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        update_status(order, int(request.data.get('status')))
        update_delivery_crew(order, request.data.get('delivery_crew_id'))
        return Response({'message': 'Order updated'}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        update_status(order, int(request.data.get('status')))
        return Response({'message': 'Order updated'}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        order = Order.objects.filter(pk=pk) 
        order.delete()
        return Response({'message': 'Order deleted'}, status=status.HTTP_200_OK)





