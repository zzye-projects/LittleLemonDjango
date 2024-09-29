from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from ..serializers import UserSerializer
from ..permissions import IsManagerAdminOr403

role_map = {'manager': 'Manager', 'delivery-crew': 'Delivery Crew'}

class UsersView(APIView):
    permission_classes = [IsManagerAdminOr403]
    
    def get(self, request, role):
        users = User.objects.filter(groups__name=role_map[role])
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
    def post(self, request, role):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)

        group = get_object_or_404(Group, name=role_map[role])
        user.groups.add(group)

        user.save()
        return Response({'message': f'User {username} added to the {role_map[role]} group'}, 
                        status=status.HTTP_201_CREATED)
    
class SingleUserView(APIView):
    permission_classes = [IsManagerAdminOr403]

    def delete(self, request, pk, role):
        group = get_object_or_404(Group, name=role_map[role])

        user = get_object_or_404(User, pk=pk)
        user.groups.remove(group)
        user.save()

        return Response({'message': f'Removed user id {pk} from {role_map[role]} group'},
                        status=status.HTTP_200_OK)
