from django.contrib import admin
from .models import Group,Members,GroupQuestion,AskQuestion,Report

admin.site.register([Group,Members,GroupQuestion,AskQuestion,Report])