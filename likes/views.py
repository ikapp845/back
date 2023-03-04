from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Like
from user.models import Profile
from question.models import Question
from .serializer import LikeSerializer
from group.models import Members,Group,Questionattended

# {"username1":"","username2":"","question":""}
@api_view(["POST"])
def like(request):
  req = request.data
  user1 = Profile.objects.get(email= req["username1"])
  user2 = Profile.objects.get(email= req["username2"])
  question = Question.objects.get(id = req["question"])
  group = Group.objects.get(id = req["group"])
  like = Like.objects.create(user_from = user1,user_to =user2,question = question,group = group )
  like.save()
  attended = Questionattended.objects.create(user = user1,question = question,group = group)
  attended.save()
  return Response("Liked")

@api_view(["GET"])
def get_likes(request,username):
  user = Profile.objects.get(email= username)
  likes = Like.objects.filter(user_to = user).order_by("time")
  serializer = LikeSerializer(likes,many = True)
  return Response(serializer.data)


@api_view(["GET"])
def get_like_count(request,group,question):
  group = Group.objects.get(id = group)
  question = Question.objects.get(id = question)
  members = Members.objects.filter(group = group)
  result = {"total":0}
  print(members)
  for items in members:
    user = items.user
    likes = Like.objects.filter(group = group,question = question,user_to = user)
    result[user.name] = {"count":likes.count()}
    result["total"] += 1

  return Response(result)







# Create your views here.
