from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import MenuItemSerializer
from ..models import MenuItem, Category
from ..permissions import IsManagerAdminOrGET
from ..helpers import get_filtered_items, get_paginated_items
from django.core.paginator import EmptyPage

class MenuItemsView(APIView):
    permission_classes = [IsManagerAdminOrGET]

    def get(self, request):
        menu_items = MenuItem.objects.select_related('category').all()
        
        # Filter menu-items
        filter_params = {
                    'featured': 'featured',
                    'title': 'title__contains',
                    'to_price':'price__lte',
                    'category_id': 'category__id'}
        menu_items = get_filtered_items(menu_items, request, filter_params)

        if menu_items:
            # Order menu-items
            order_params = request.query_params.get('ordering')
            if order_params: menu_items = menu_items.order_by(*order_params.split(','))

            # Apply pagination
            try:
                menu_items = get_paginated_items(menu_items, request)
            except EmptyPage:
                return Response({'message':'Invalid page'}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message':'No menu-items found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):        
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            get_object_or_404(Category, pk=request.data.get('category_id'))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Overriden status code from 405 to 403
    def put(self, request):
        return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request):
        return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

class SingleMenuItemView(APIView):
    permission_classes = [IsManagerAdminOrGET]
    
    def get(self, request, pk):
        menu_item = get_object_or_404(MenuItem.objects.select_related('category'), pk=pk)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        menu_item.delete()
        return Response({'message': 'Deleted menuitem {}'.format(pk)}, status=status.HTTP_200_OK)
        
    # Overriden status code from 405 to 403
    def post(self, request):
        return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    