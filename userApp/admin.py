from django.contrib import admin
from .models import Users, Company

admin.site.register(Company)
admin.site.register(Users)