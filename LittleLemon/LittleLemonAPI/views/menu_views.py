from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..serializers import MenuItemSerializer
from ..models import MenuItem
from ..permissions import IsManagerAdminOrGET
from ..helpers import CustomPageSize

class MenuViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerAdminOrGET]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    pagination_class = CustomPageSize

    filterset_fields = {
        'title': ['exact', 'icontains'],
        'price' : ['lte'],
        'featured': ['exact'],
        'category__id': ['exact']
    }

    ordering_fields = ['title', 'price', 'featured', 'category__id']
    ordering = ['title']