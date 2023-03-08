from django.contrib import admin
from .models import Group,Members,GroupQuestion,Questionattended,AskQuestionAttended,AskQuestion

admin.site.register([Group,Members,GroupQuestion,Questionattended,AskQuestionAttended,AskQuestion])