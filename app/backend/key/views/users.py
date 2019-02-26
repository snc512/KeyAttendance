from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import UserSerializer, UserSerializerEdit

class Users(APIView):

    def validatePost(self, request):
        if not 'username' in request.data or not 'password' in request.data:
            return False
        try:
            User.objects.get(username=request.data['username'])
            return False
        except:
            return True
        return True
    
    def validatePatch(self, request):
        if not 'id' in request.data:
            return False
        try:
            User.objects.get(pk=request.data['id'])
        except:
            return False
        return True

    def validateDelete(self, request):
        if not 'id' in request.query_params:
            return False
        try:
            User.objects.get(pk=request.query_params['id'])
        except:
            return False
        return True

    def get(self, request):
        if not request.user.has_perm('key.view_user'):
            return Response({'error':'You are not authorized to view users.'}, status='401')
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, content_type='application/json')

    def patch(self, request):
        if not request.user.has_perm('key.change_user'):
            return Response({'error':'You are not authorized to change users.'}, status='401')
        if not self.validatePatch(request):
            return Response({'error':'Invalid Parameters'}, status='400')
        user = User.objects.get(pk=request.data['id'])
        serializer = UserSerializer(user)
        if request.user.id == user.id and request.data['is_active'] != user.is_active:
            return Response({'error':'Users are not authorized to inactivate their own accounts'}, status='401')
        if request.user.id == user.id and request.data['groups'] != serializer.data['groups']:
            return Response({'error':'Users are not authorized to change their own user role'}, status='401')
        serializer = UserSerializerEdit(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if not request.user.has_perm('key.add_user'):
            return Response({'error':'You are not authorized to create users.'}, status='401')
        if not self.validatePost(request):
            return Response({'error':'Invalid Parameters'}, status='400')
        serializer = UserSerializerEdit(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not request.user.has_perm('key.delete_user'):
            return Response({'error':'You are not authorized to delete users.'}, status='401')
        if request.user.id == int(request.query_params['id']):
            return Response({'error': 'Users are not authorized to delete their own accounts.'}, status='401')
        if not self.validateDelete(request):
            return Response({'error':'Invalid Parameters'}, status='400')

        user = User.objects.get(pk=request.query_params['id'])
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
