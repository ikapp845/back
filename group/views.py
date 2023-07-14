from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Group,Members,AskQuestion,GroupQuestion
from django.shortcuts import render
from user.models import Profile
from .serializers import GroupQuestionSerializer,MemberSerializer,GroupQuestionSerializer
from datetime import datetime
from django.utils.timezone import localtime 
from .serializers import UserGroupsSerializer
from django.utils import timezone
from .models import AskQuestion,Report
import json
from django.core.cache import cache
from django.contrib.auth.models import User
from questions import questions
import random


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):
  with transaction.atomic():
    req = request.data
    group = Group.objects.create(name= req["name"],admin_id = request.user.username)
    group.save()

    
    member = Members.objects.create(group = group,user_id = request.user.username)
    member.save()

  return Response(group.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
  req = request.data

  try:
    member = Members.objects.get(group_id = req["group"],user_id= request.user.username)
    return Response("User already in group")
  except:
    try:
      member = Members.objects.create(group_id = req["group"],user_id = request.user.username)
      return Response("Success")
    except:
      return Response("Group does not exist")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_group_members_contact(request):
    with transaction.atomic():
        contacts = request.data["selected"]
        group = Group.objects.get(id=request.data["group"])
        members = [Members(group_id = request.data["group"], user_id = user) for user in contacts]
        l = len(members)
        group.count += l
        group.save()
        Members.objects.bulk_create(members)
    return Response("Added")


def compare_dates(desired,now):
  if desired.year == now.year:
    if desired.month == now.month:
      if desired.day == now.day:
        if (now.hour - desired.hour) >= 1:
          return True
        else:
          return False
      else:
        return True
    else:
      return True
  else:
    return True


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_members(request,group):
  members = Members.objects.select_related("user","group").filter(group_id = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_main(request,group,email):

  def group_members(gp):
    members = Members.objects.select_related("user","group").filter(group_id = gp)
    serializer = MemberSerializer(members,many = True)
    return serializer.data

  def group_questions(group):
    question_list = GroupQuestion.objects.filter(group_id = group)
    now = timezone.now()
    before = now - timezone.timedelta(hours = 1)
    if not question_list or compare_dates(question_list[len(question_list) - 1].time, now) == True:
      if question_list:
        before = question_list[0].time 
        question_list.delete()
      user_que = AskQuestion.objects.filter(group_id = group,time__gt = before)[:10]
      user_que_count = len(user_que)
      res = random.sample(list(questions.values()),10-user_que_count)
      question_list = list(user_que) + list(res)
      a = []
      for items in question_list:
        question = GroupQuestion()
        question.question_id = items['id']
        question.question = items['question']
        question.source = 'user' if isinstance(items, AskQuestion) else 'ik'
        question.group_id = group
        a.append(question)
      group_question = GroupQuestion.objects.bulk_create(a,10)
      question_list = group_question
      time = question_list[0].time
    else:
      time = question_list[0].time
    serializer = GroupQuestionSerializer(question_list,many = True)
    return serializer.data,str(time)
    


  group_mem  = group_members(group)
  group_ques,time= group_questions(group)
  final = {"members":group_mem,"questions":group_ques,"time" : time}
  return Response(final)

 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave(request):
  req = request.data
  with transaction.atomic():
    group = Group.objects.get(id =req["group"] )
    user = Profile.objects.get(email= request.user.username)
    if group.admin == user:
      try:
        new_admin = Members.objects.filter(group = items).order_by("added")[1]
        items.admin = new_admin.user
        items.save()
      except IndexError:
        items.delete()
    mem = Members.objects.get(group = group,user = user)
    mem.delete()
  return Response("removed")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_groups(request,username):
  members = Members.objects.select_related("group","user").filter(user_id = username).defer("added")
  serializer = UserGroupsSerializer(members,many  = True)
  return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_question(request):
  req = request.data
  group = Group.objects.get(id = req["group"])
  question = AskQuestion.objects.create(group = group,question = req["question"],user = Profile.objects.get(email = request.user.username))
  question.save()
  return Response("Question Added")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report(request,group,question):
  group = Group.objects.get(id = group)
  question = AskQuestion.objects.get(id = question)
  report = Report.objects.create(group = group,question = question)
  report.save()
  return Response("Reported")

from django.core.cache import cache

@api_view(["GET"])
def add(request):
  q = []

  for items in q:
    a = Question.objects.create(question = items)
    a.save()
  return Response("saved")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_member(request):
  req = request.data
  user = Profile.objects.get(email = req["email"])
  group = Group.objects.get(id = req["group"])
  members = Members.objects.get(user = user,group = group).delete()
  members = Members.objects.select_related("user","group").filter(group = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def delete_account(request):
  user = User.objects.get(username = request.user.username)
  prof = Profile.objects.get(email = request.user.username)
  groups = Group.objects.filter(admin = prof)
  if groups.exists():
    for items in groups:
      try:
        new_admin = Members.objects.filter(group = items).order_by("added")[1]
        items.admin = new_admin.user
        items.save()
      except IndexError:
        items.delete()
  user.delete()
  prof.delete()
  return Response("Deleted")


