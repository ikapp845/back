from django.contrib import admin
from .models import Group,Members,GroupQuestion,Questionattended

admin.site.register([Group,Members,GroupQuestion,Questionattended])