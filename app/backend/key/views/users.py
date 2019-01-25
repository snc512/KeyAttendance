from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import UserSerializer, UserSerializerEdit
from rest_framework.decorators import permission_classes

class Users(APIView):
    permission_classes = (permissions.IsAdminUser,)

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

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, content_type='application/json')

    def patch(self, request):
        if not self.validatePatch(request):
            return Response({'error':'Invalid Parameters'}, status='400')

        user = User.objects.get(pk=request.data['id'])
        serializer = UserSerializerEdit(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if not self.validatePost(request):
            return Response({'error':'Invalid Parameters'}, status='400')
        serializer = UserSerializerEdit(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)