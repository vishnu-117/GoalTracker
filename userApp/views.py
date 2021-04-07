from django.shortcuts import render
from django.db.models import Q
from .models import Users, Company, Goal, SubGoal, Chat
from .serializers import UserSerializer, LoginSerializer, CompanySerializer, GoalSerializer, SubGoalSerializer, \
    ChatSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from datetime import date, datetime, timedelta
from django.utils import timezone

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
        query = self.request.query_params
        if self.request.user.user_type == 'Employer' and self.request.method.lower() == 'get':
            # if query.get('is_employee') == 'false':
            if query.get('is_employee') == 'false':
                subgoal_qs = SubGoal.objects.filter(goal__company=self.request.user.company).filter(is_personal_goal=True)
                subgoal_id = [subgoal.goal.id for subgoal in subgoal_qs]
                return Goal.objects.filter(id__in=subgoal_id)
            return Goal.objects.filter(created_by=self.request.user)
        elif self.request.user.user_type == 'Employee' and self.request.method.lower() == 'get':
            # print(query.get('is_employee'))
            if query.get('is_employee') == 'true':
                subgoal_qs = SubGoal.objects.filter(user=self.request.user).filter(is_personal_goal=True)
                subgoal_id = [subgoal.goal.id for subgoal in subgoal_qs]
                return Goal.objects.filter(id__in=subgoal_id)

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
        expert = self.request.query_params
        user_list = Users.objects.filter(company=self.request.user.company)
        if expert:
            return user_list.filter(user_type='Expert')
        return user_list

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class graphApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data = {}
        if request.user.user_type == 'Employee' or request.user.user_type == 'Expert':
            subgoal_list = SubGoal.objects.filter(user=self.request.user)
            subgoal_count = subgoal_list.count()
            rescheduled = subgoal_list.filter(is_reschedule=True).count()
            completed = subgoal_list.filter(is_completed=True).count()
            pending_subgoal_name = list(subgoal_list.filter(Q(is_completed=False) & Q(is_reschedule=False)).values_list('title'))
            completed_subgoal_name = list(subgoal_list.filter(is_completed=True).values_list('title'))
            rescheduled_subgoal_name = list(subgoal_list.filter(is_reschedule=True).values_list('title'))
            data['completed'] = completed
            data['completed_goal_name'] = [completed_subgoal_name[0] for completed_subgoal_name in completed_subgoal_name]
            data['rescheduled'] = rescheduled
            data['rescheduled_goal_name'] = [rescheduled_subgoal_name[0] for rescheduled_subgoal_name in rescheduled_subgoal_name]
            data['pending'] =  subgoal_count - (completed + rescheduled)
            data['pending_goal_name'] = [pending_subgoal_name[0] for pending_subgoal_name in pending_subgoal_name]
            return Response(data)
        else:
            goal_list = Goal.objects.filter(created_by=self.request.user)
            goal_count = goal_list.count()
            rescheduled = goal_list.filter(is_reschedule=True).count()
            pending_subgoal_name = list(goal_list.filter(Q(is_completed=False) & Q(is_reschedule=False)).values_list('goal_name'))
            completed_subgoal_name = list(goal_list.filter(is_completed=True).values_list('goal_name'))
            rescheduled_subgoal_name = list(goal_list.filter(is_reschedule=True).values_list('goal_name'))
            completed = goal_list.filter(is_completed=True).count()
            data['completed'] = completed
            data['completed_goal_name'] = [completed_subgoal_name[0] for completed_subgoal_name in completed_subgoal_name]
            data['rescheduled'] = rescheduled
            data['rescheduled_goal_name'] = [rescheduled_subgoal_name[0] for rescheduled_subgoal_name in rescheduled_subgoal_name]
            data['pending'] =  goal_count - (completed + rescheduled)
            data['pending_goal_name'] = [pending_subgoal_name[0] for pending_subgoal_name in pending_subgoal_name]
            return Response(data)


class ChatView(ListModelMixin,
                CreateModelMixin,
                DestroyModelMixin,
                GenericAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        goal_id = self.request.query_params['goal_id']
        return Chat.objects.filter(goal=goal_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data = {}
        if request.user.user_type == 'Employee' or request.user.user_type == 'Expert':
            subgoal_list = SubGoal.objects.filter(user=self.request.user)
            subgoal_list = list(subgoal_list.filter(end_date__date__lte=timezone.now() + timedelta(2)).values_list('title'))
            data['subgoal_list'] = [subgoal_list[0] for subgoal_list in subgoal_list]
            return Response(data)
        else:
            subgoal_list = [goal.id for goal in Goal.objects.filter(created_by=self.request.user)]
            subgoal_list = SubGoal.objects.filter(goal__id__in=subgoal_list)
            subgoal_list = list(subgoal_list.filter(end_date__date__lte=timezone.now() + timedelta(2)).values_list('title', 'end_date', named=True))
            data['subgoal_list'] = [subgoal_list[0] for subgoal_list in subgoal_list]
            return Response(data)