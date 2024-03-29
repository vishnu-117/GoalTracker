from rest_framework import serializers
from django.contrib.auth import login, authenticate
from .models import Company, Users, Goal, SubGoal, Chat

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


class SubGoalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y'], format='%d-%m-%Y', required=False)
    end_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y'], format='%d-%m-%Y', required=False)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = SubGoal
        exclude = ['goal', ]

    def get_user_name(self, obj):
        return obj.user.name
class GoalSerializer(serializers.ModelSerializer):
    subgoal = SubGoalSerializer(many=True, required=False)
    start_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y'], format='%d-%m-%Y', required=False)
    end_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y'], format='%d-%m-%Y', required=False)

    class Meta:
        model = Goal
        exclude = []

    def create(self, validated_data):
        user = self.context['request'].user
        subgoal = validated_data.pop('subgoal', [])
        goal = Goal.objects.create(**validated_data)
        goal.created_by = user
        goal.company = user.company
        goal.save()
        if subgoal:
            subgoal = subgoal[0]
            SubGoal.objects.create(goal=goal, **subgoal)
        return goal

    def update(self, instance, validated_data):
        subgoal = validated_data.pop('subgoal')
        for subgoal_data in subgoal:
            pk = subgoal_data.get('id')
            if pk:
                subgoal = SubGoal.objects.get(id=pk)
                for i in subgoal_data:
                    setattr(subgoal, i, subgoal_data[i])
                subgoal.save()
            else:
                SubGoal.objects.create(goal=instance, **subgoal_data)
        instance = super(GoalSerializer, self).update(instance, validated_data)
        return instance


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        exclude = []