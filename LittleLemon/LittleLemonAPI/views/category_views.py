from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..serializers import CategorySerializer
from ..models import Category
from ..permissions import IsManagerAdminOrGET
from ..helpers import CustomPageSize

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerAdminOrGET]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    pagination_class = CustomPageSize

    filterset_fields = {
        'slug': ['exact', 'icontains'],  
        'title': ['exact', 'icontains'],
    }

    ordering_fields = ['slug', 'title']
    ordering = ['title'] 