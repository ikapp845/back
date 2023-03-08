

# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Group
from .models import Members,AskQuestion
from .models import GroupQuestion,Questionattended,AskQuestionAttended
from question.models import Question
from django.shortcuts import render
from user.models import Profile
from .serializers import GroupQuestionSerializer,MemberSerializer
from datetime import datetime
from django.utils.timezone import localtime 
from .serializers import UserGroupsSerializer
from django.utils import timezone
from .models import AskQuestion



@api_view(["POST"])
def create_group(request):
  req = request.data

  group = Group.objects.create(name= req["name"])
  group.save()

  user = Profile.objects.get(email = req["username"])
  member = Members.objects.create(group = group,user = user)
  member.save()

  return Response("Group created")


@api_view(['POST'])
def join_group(request):
  req = request.data
  try:
    group = Group.objects.get(id = req["group"])
    user = Profile.objects.get(email= req["username"])
  except:
    return Response("Group does not exist")

  try:
    member = Members.objects.get(group = group,user= user)
    print(member)
    return Respone("User already in group")
  except:
    member = Members.objects.create(group = group,user = user)
    member.save()
    return Response("Success")

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

def get_count(group,user,question):
  count = 10
  ask_question = AskQuestion.objects.filter(group = group)
  for items in ask_question:
    try:
      a = AskQuestionAttended.objects.get(user=user,question = items)
    except:
      question.append([items.question,"user"])
      count -= 1
  return count

@api_view(["GET"])
def group_question(request,group,username):
  gp = Group.objects.get(id = group)
  user = Profile.objects.get(email= username)
  gqs = GroupQuestion.objects.filter(group = gp)
  question = []
  if not gqs:
    count = get_count(gp,user,question)
    question1 = Question.objects.order_by("?")[:count]
    for items in question1:
      gq = GroupQuestion.objects.create(group = gp,question = items)
      gq.save()
    gqs = GroupQuestion.objects.filter(group = gp)
  else:
    gq = gqs[len(gqs) -1]
    desired_datetime = gq.time
    now = timezone.now()
    if compare_dates(desired_datetime,now):
          attended = GroupQuestion.objects.filter(group = gp)
          attended.delete()
          GroupQuestion.objects.filter(group = gp).delete()
          questionattended = Questionattended.objects.filter(group = gp)
          questionattended.delete()
          count = get_count(gp,user,question)
          question1 = Question.objects.order_by("?")[:count]
          for items in question1:
            gq = GroupQuestion.objects.create(group = gp,question = items)
            gq.save()
          gqs = GroupQuestion.objects.filter(group = gp)
    else:
      ask_question = AskQuestion.objects.filter(group = group)
      for items in ask_question:
        try:
          a = AskQuestionAttended.objects.get(user=user,question = items)
        except:
          question.append([items.question,"user"])
  for items in gqs:
    try:
      qat = Questionattended.objects.get(user = user,group = gp,question = items.question)
    except:
      question.append([items.question.id,items.question.question,"ik"])
  if question == []:
    return (String(now.minute - desired.minute) + " " + String(now.second - desired.second))

  return Response(question)


# Create your views here.
@api_view(["GET"])
def group_members(request,group):
  group = Group.objects.get(id = group)
  members = Members.objects.filter(group = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)


#{"username":"","group":""} 
@api_view(["POST"])
def leave(request):
  req = request.data
  group = Group.objects.get(id =req["group"] )
  user = Profile.objects.get(email= req["username"])
  mem = Members.objects.get(group = group,user = user)
  mem.delete()
  return Response("removed")

@api_view(["GET"])
def user_groups(request,username):
  user = Profile.objects.get(email= username)
  members = Members.objects.filter(user = user)
  serializer = UserGroupsSerializer(members,many  = True)
  return Response(serializer.data)


def total_members_count(group):
  members = Members.objects.filter(group = group)
  return members.count


@api_view(["POST"])
def add_question(request):
  req = request.data
  group = Group.objects.get(id = req["group"])
  question = AddQuestion.objects.create(group = group,question = req["question"],total_members = total_members_count(group))
  question.save()
  return Response("Question Added")
