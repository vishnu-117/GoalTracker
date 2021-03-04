from rest_framework import serializers
from django.contrib.auth import login, authenticate
from .models import Company, Users

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        exclude = []

class UserSerializer(serializers.ModelSerializer):
    # company = CompanySerializer(required=False)

    class Meta:
        model = Users
        exclude = ['is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'password', 'last_login']


    def create(self, validated_data):
        user = Users.objects.create(**validated_data)
        user.password1 = '12345'
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=30, min_length=5)
    password1 = serializers.CharField(max_length=12, min_length=4, required=False)

    FIELD_VALIDATION_ERRORS = {}
    NON_FIELD_ERRORS = {}

    def validate(self, data):
        email = data.get('email')
        password1 = data.get('password1')
        request = self.context.get('request')

        users = Users.objects.filter(email=email,
                                     is_active=True,
                                     password1=password1)
        if users:
            user = users.latest('id')
            login(request, user)
            return data
        else:
            raise serializers.ValidationError({'error': 'email or password is not correct'})
        return data
