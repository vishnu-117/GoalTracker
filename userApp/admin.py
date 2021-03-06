from django.contrib import admin
from .models import Users, Company, Goal, SubGoal

admin.site.register(Company)
admin.site.register(Users)
admin.site.register(Goal)
admin.site.register(SubGoal)

