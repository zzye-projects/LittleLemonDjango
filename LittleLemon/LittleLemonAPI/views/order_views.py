from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from ..serializers import OrderSerializer
from ..models import Cart, Order, OrderItem
from ..helpers import CustomPageSize
from ..permissions import OrderPermissions
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

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
        serializer = self.get_serializer(order)
        return Response( serializer.data, status=status.HTTP_200_OK )
        
    def update(self, request, *args, **kwargs):
        return self.custom_update(
            request, 
            allow_fields = {'delivery_crew_id', 'status', 'date'}, 
            partial=True
        )

    def partial_update(self, request, *args, **kwargs):
        allow_fields = {}
        if request.user.groups.filter(name='Manager').exists(): 
            allow_fields = {'delivery_crew_id', 'status', 'date'}
        elif request.user.groups.filter(name='Delivery Crew'): 
            allow_fields = {'status'}
        
        return self.custom_update( request, allow_fields, partial=True)

    def custom_update(self, request, allow_fields, partial):
        fields = list(request.data.keys())
        [request.data.pop(field) for field in fields if field not in allow_fields]

        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)