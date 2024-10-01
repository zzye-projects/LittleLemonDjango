from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..serializers import OrderSerializer
from ..models import Cart, Order, OrderItem
from rest_framework.exceptions import ValidationError
from ..helpers import CustomPageSize
from ..permissions import OrderPermissions
from django.utils import timezone
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
        
def update_status(order, status_code):
    if status_code in (0, 1): 
        order.status=status_code
        order.save()
    raise ValidationError('Invalid status code')   
     
def update_delivery_crew(order, delivery_crew_id):
    delivery_crew = User.objects \
        .filter(pk=delivery_crew_id, groups__name='Delivery Crew') \
        .first()
    if delivery_crew_id and not delivery_crew:
        raise ValidationError('Invalid user id for the delivery crew')
    elif delivery_crew_id: order.delivery_crew=delivery_crew
    order.save()

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    pagination_class = CustomPageSize
    permission_classes = [OrderPermissions]

    filterset_fields = {
        'user__id': ['exact'],  
        'delivery_crew__id': ['exact'],
        'status': ['exact'],
        'total' : ['lte'],
        'date' : ['lte', 'gte']
    }

    ordering_fields = ['user__id', 'delivery_crew__id', 'status','total', 'date']
    ordering = ['user__id'] 

    def get_queryset(self):
        user, user_groups = self.request.user, self.request.user.groups
        if not user_groups.first():
            return Order.objects.filter(user=user)
        elif user_groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user_groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return []
    
    def create(self, request, *args, **kwargs):
        user = request.user
        carts = Cart.objects.filter(user=user)
        if not len(carts): 
            return Response({'message': 'Your cart is empty. No orders to be submitted'}, \
                            status=status.HTTP_204_NO_CONTENT)
        
        order, created = Order.objects.get_or_create(user=user)
        if not order.date: order.date=timezone.now().date()

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
        serializer = OrderSerializer(order)
        return Response( serializer.data, status=status.HTTP_200_OK )
        
# class SingleOrderView(APIView):
        
#     def put(self, request, pk):
#         order = get_object_or_404(Order, pk=pk)
#         update_status(order, int(request.data.get('status')))
#         update_delivery_crew(order, request.data.get('delivery_crew_id'))
#         return Response({'message': 'Order updated'}, status=status.HTTP_200_OK)
    
#     def patch(self, request, pk):
#         order = get_object_or_404(Order, pk=pk)
#         update_status(order, int(request.data.get('status')))
#         return Response({'message': 'Order updated'}, status=status.HTTP_200_OK)

#     def delete(self, request, pk):
#         order = Order.objects.filter(pk=pk) 
#         order.delete()
#         return Response({'message': 'Order deleted'}, status=status.HTTP_200_OK)