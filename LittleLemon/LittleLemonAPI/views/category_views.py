from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import CategorySerializer
from ..models import Category
from ..globals import *
from ..permissions import IsManagerAdminOrGET
from ..helpers import get_filtered_items, get_paginated_items
from django.core.paginator import EmptyPage

class CategoryView(APIView):
    permission_classes = [IsManagerAdminOrGET]

    def get(self, request):
        categories = Category.objects.all()
        
        # Filter categories
        filter_params = { 'title': 'title__contains', 'slug':'slug__contains'}
        categories = get_filtered_items(categories, request, filter_params)

        if categories:
            # Order menu-items
            order_params = request.query_params.get('ordering')
            if order_params: categories = categories.order_by(*order_params.split(','))

            # Apply pagination
            try:
                categories = get_paginated_items(categories, request)
            except EmptyPage:
                return Response({'message':'Invalid page'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message':'No categories found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)