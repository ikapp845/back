from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Group,Members,AskQuestion,GroupQuestion
from question.models import Question
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):
  with transaction.atomic():
    req = request.data
    user = Profile.objects.get(email = request.user.username)
    group = Group.objects.create(name= req["name"],admin = user)
    group.save()

    
    member = Members.objects.create(group = group,user = user)
    member.save()

  return Response(group.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
  req = request.data
  try:
    group = Group.objects.get(id = req["group"])
    user = Profile.objects.get(email= request.user.username)
  except:
    return Response("Group does not exist")

  try:
    member = Members.objects.get(group = group,user= user)
    return Respone("User already in group")
  except:
    member = Members.objects.create(group = group,user = user)
    member.save()
    return Response("Success")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_group_members_contact(request):
    with transaction.atomic():
        contacts = request.data["selected"]
        group = Group.objects.get(id=request.data["group"])
        users = Profile.objects.filter(email__in=contacts)
        members = [Members(group=group, user=user) for user in users]
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
  group = Group.objects.get(id = group)
  members = Members.objects.select_related("user","group").filter(group = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def group_main(request,group,email):

  def group_members(gp):
    members = Members.objects.select_related("user","group").filter(group = gp)
    group_length = members.count()
    serializer = MemberSerializer(members,many = True)
    return serializer.data,group_length

  def group_questions(gp,user,group,group_length):
    question_list = GroupQuestion.objects.filter(group = gp)
    now = timezone.now()
    one_hour_ago = now - timezone.timedelta(hours = 1)
    before = one_hour_ago
    if not question_list or compare_dates(question_list[len(question_list) - 1].time, now) == True:
      if question_list:
        before = question_list[0].time 
        question_list.delete()
      user_que = AskQuestion.objects.filter(group = gp,time__gt = before)[:10]
      user_que_count = len(user_que)
      ik_que = Question.objects.filter().order_by("?")[:10-user_que_count]
      question_list = list(user_que) + list(ik_que)
      a = []
      for items in question_list:
        question = GroupQuestion()
        question.question_id = items.id
        question.question = items.question
        question.source = 'user' if isinstance(items, AskQuestion) else 'ik'
        question.group = gp
        a.append(question)
      group_question = GroupQuestion.objects.bulk_create(a,10)
      question_list = group_question
      time = question_list[0].time
    else:
      time = question_list[0].time
    serializer = GroupQuestionSerializer(question_list,many = True)
    return serializer.data,str(time)
    


  gp =  Group.objects.get(id = group)
  # user = Profile.objects.get(email = request.user.username)
  user = Profile.objects.get(email = "9562267229")
  group_mem,group_length  = group_members(gp)
  group_ques,time= group_questions(gp,user,group,group_length = group_length)
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
  user = Profile.objects.get(email= username)
  members = Members.objects.select_related("group").filter(user = user)
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
  q = Question.objects.using("question").all()

  for items in q:
    a = Question.objects.create(question = items.question)
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


