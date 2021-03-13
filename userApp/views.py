from django.shortcuts import render
from .models import Users, Company, Goal, SubGoal
from .serializers import UserSerializer, LoginSerializer, CompanySerializer, GoalSerializer, SubGoalSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView


class CompanyListAPIView(ListModelMixin, GenericAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = []


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserSignupView(CreateModelMixin, GenericAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = []


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
def LoginAPI(request):
    loginserializer = LoginSerializer(
        data=request.data, context={'request': request})
    if not loginserializer.is_valid():
        return Response(data=loginserializer.errors, status=403)

    token, created = Token.objects.get_or_create(user=request.user)
    user_data = UserSerializer(request.user).data

    return Response(data = {'user_data':user_data,
                            'access_token': str(token)}, status=200)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def LogoutAPI(request):
    token, created = Token.objects.get_or_create(user=request.user)
    token.delete()
    logout(request)
    return APIResponse(status=200)

class GoalView(ListModelMixin,
                       CreateModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       DestroyModelMixin,
                       GenericAPIView):
    queryset = Goal.objects.filter()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        if self.request.user.user_type == 'Employer' and self.request.method.lower() == 'get':
            return Goal.objects.filter(created_by=self.request.user.created_by)
        elif self.request.user.user_type == 'Employee' and self.request.method.lower() == 'get':
            subgoal_qs = SubGoal.objects.filter(user=self.request.user)
            subgoal_id = [subgoal.goal.id for subgoal in subgoal_qs]
            return Goal.objects.filter(id__in=subgoal_id)
        else:
            return Goal.objects.filter()


    def create(self, request, *args, **kwargs):
        serialized_obj = GoalSerializer(data=request.data,
                                                context={'user': request.user, 'request': request})
        if serialized_obj.is_valid():
            obj = serialized_obj.save()
        else:
            return Response(serialized_obj.errors, status=400)
        return Response(serialized_obj.data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.errors, status=400)
        self.perform_update(serializer)
        instance.refresh_from_db()
        return Response(serializer.data, status=200)

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    #
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    #
    # def delete(self, request, *args, **kwargs):
    #     return self.destroy(request, *args, **kwargs)

class UserList(ListModelMixin, GenericAPIView):
    queryset = Users.objects.filter()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        # company_id = self.request.query_params['company_id']
        return Users.objects.filter(company=self.request.user.company)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
