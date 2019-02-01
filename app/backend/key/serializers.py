from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from .models import Students, AttendanceItems, Activity, StudentSuggestions

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'id',
            'first_attendance',
            'number_visits',
            'student_key'
        )
        model = Students

class AttendanceItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'student_id',
            'date',
            'time',
            'activity_id',
            'id',
        )
        model = AttendanceItems

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'is_staff', 'last_login')

class UserSerializerCreate(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('username', 'password', 'is_staff', 'last_login')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'ordering',
            'is_showing',
            'activity_id'
        )
        model = Activity

class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'student_id',
            'match_name',
            'match_key'
        )
        model = StudentSuggestions