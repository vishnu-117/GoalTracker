from django.shortcuts import render
from .models import Users, Company
from .serializers import UserSerializer, LoginSerializer, CompanySerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt


class CompanyListAPIView(ListModelMixin, GenericAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserSignupView(CreateModelMixin, GenericAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.create(request, *args, **kwargs)
            return Response(status=200, data=serializer.data)
        return Response(serializer.errors, status=400)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()


@api_view(['POST'])
@csrf_exempt
def LoginAPI(request):
    loginserializer = LoginSerializer(
        data=request.data, context={'request': request})
    if not loginserializer.is_valid():
        return Response(data=loginserializer.errors, status=403)

    user_data = UserSerializer(request.user).data

    return Response(user_data, status=200)

