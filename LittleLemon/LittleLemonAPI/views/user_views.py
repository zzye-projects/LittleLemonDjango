from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from ..serializers import UserSerializer
from ..permissions import IsManagerAdminOr403

class UsersView(APIView):
    permission_classes = [IsManagerAdminOr403]
    
    def get(self, request, role):
        users = User.objects.filter(groups__name=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
    def post(self, request, role):
        group = get_object_or_404(Group, name=role)
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        user.groups.set([group])
        user.save()
        return Response({'message': 'User {} added to the {} group'.format(username, role)}, 
                        status=status.HTTP_201_CREATED)
    
class SingleUserView(APIView):
    permission_classes = [IsManagerAdminOr403]

    def delete(self, request, pk, role):
        user = get_object_or_404(User, pk=pk)
        user.groups.clear()
        user.save()
        return Response({'message': 'Removed user id {} from manager group'.format(pk)}, \
                        status=status.HTTP_200_OK)