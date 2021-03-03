from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UsersManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, first_name, password=None, *args, **kwargs):
        user = self.model(
            email=email,
            first_name=first_name,
            *args, **kwargs
        )
        if password is not None:
            user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, *args, **kwargs):
        user = self.create_user(email, first_name, *args, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.admin = True
        user.save(using=self._db)
        return user

USER_TYPE = (
    ('Empoyee', 'Empoyee'),
    ('Empoyer', 'Empoyer'),
    ('Expert', 'Expert')
)


class Users(AbstractBaseUser, PermissionsMixin):
    username = None
    first_name = models.CharField(
        'Name', max_length=128, null=False, blank=False)
    last_name = models.CharField(max_length=128, null=False, blank=False)
    email = models.CharField(max_length=16, unique=True, null=False, blank=False)
    # email = models.EmailField(null=True, blank=True)
    # company_id = models.ForeignKey(
    #     'Companies', null=True, on_delete=models.CASCADE)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='Empoyer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = UsersManager()

