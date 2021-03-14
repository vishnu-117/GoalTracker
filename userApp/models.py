from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UsersManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, password=None, *args, **kwargs):
        user = self.model(
            email=email,
            name=name,
            *args, **kwargs
        )
        if password is not None:
            user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, *args, **kwargs):
        user = self.create_user(email, name, *args, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.admin = True
        user.save(using=self._db)
        return user

USER_TYPE = (
    ('Employee', 'Employee'),
    ('Employer', 'Employer'),
    ('Expert', 'Expert')
)

GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other')
)

class Users(AbstractBaseUser, PermissionsMixin):
    username = None
    name = models.CharField(max_length=128, null=False, blank=False)
    email = models.CharField(max_length=50, unique=True, null=False, blank=False)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    department = models.CharField(max_length=150, null=True, blank=True)
    skills = models.CharField(max_length=150, null=True, blank=True)
    experience = models.CharField(max_length=150, null=True, blank=True)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(choices=USER_TYPE, max_length=100, default='Employee')
    gender = models.CharField(choices=GENDER, max_length=100, default='Male')
    password1 = models.CharField(max_length=100, null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UsersManager()

class Company(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class Goal(models.Model):
    created_by = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey('company', on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_reschedule = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class SubGoal(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True)
    goal = models.ForeignKey('Goal', on_delete=models.CASCADE, related_name='subgoal')
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_personal_goal = models.BooleanField(default=False)
    is_reschedule = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Chat(models.Model):
    goal = models.ForeignKey('Goal', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return self.message
