from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, Permission, User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import GroupSerializer, UserSerializer

class Groups(APIView):

    def validatePost(self, request):
        if not 'username' in request.data:
            return False
        if 'permissions' in request.data:
            for perm in request.data['permissions']:
                try:
                    Permission.objects.get(pk=perm)
                except:
                    return False
        return True
    
    def validatePatch(self, request):
        if not 'id' in request.data:
            return False
        try:
            Group.objects.get(pk=request.data['id'])
        except:
            return False
        return True

    def validateDelete(self, request):
        if not 'id' in request.query_params:
            return False
        try:
            Group.objects.get(pk=request.query_params['id'])
        except:
            return False
        return True

    def get(self, request):
        if not request.user.has_perm('auth.view_user') and not request.user.has_perm('auth.view_group'):
            return Response({'error':'You are not authorized to view user groups.'}, status='401')
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, content_type='application/json')

    def patch(self, request):
        if not request.user.has_perm('auth.change_group'):
            return Response({'error':'You are not authorized to update user groups.'}, status='401')
        group = Group.objects.get(pk=request.data['id'])
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if not request.user.has_perm('auth.add_group'):
            return Response({'error':'You are not authorized to create user groups.'}, status='401')
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not request.user.has_perm('auth.delete_group'):
            return Response({'error':'You are not authorized to delete user groups.'}, status='401')
        if not self.validateDelete(request):
            return Response({'error':'Invalid Parameters'}, status='400')
        group_id = request.query_params['id']
        group = Group.objects.get(pk=group_id)
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        inactive_users = []
        for user in user_serializer.data:
            if int(group_id) in user['groups']:
                inactive_users.append(user['id'])
        for user_id in inactive_users:
            user = users.get(pk=user_id)
            user.is_active = False
            user.save()
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
