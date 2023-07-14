from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Like,AskedLike
from user.models import Profile
from .serializer import LikeSerializer,FriendLikeSerializer,FromUserSerializer
from group.models import Members,Group,AskQuestion
from datetime import datetime
from django.db import transaction
from django.db.models import Count, Q, Value,F
from django.db.models.functions import Coalesce

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def like(request):
  req = request.data
  username1 = req["username1"]
  username2 = req["username2"]
  question_id = req["question"]
  profile_qs = Profile.objects.filter(email__in=[username1, username2])
  profiles = {profile.email: profile for profile in profile_qs}
  question = question_id
  group = Group.objects.get(id = req["group"])
  members = Members.objects.filter(group = group)

  like = Like.objects.create(
      user_from=profiles[username1],
      user_to=profiles[username2],
      question=question,
      group=group,
  )
  profiles[username2].total_likes = profiles[username2].total_likes + 1
  profiles[username2].save()

  likes = Like.objects.filter(group=group, question=question)
  result = (
      likes.values('user_to__name',"user_to__email")
      .annotate(count=Count('id'))
      .values('user_to__name','count',"user_to__email")
      .order_by("-count")
  )

  b = 0
  a = profiles[username1].coins 
  if result[0]["user_to__email"] == username2:
    a = profiles[username1].coins + group.count
    b = group.count
    profiles[username1].coins = a
    profiles[username1].save()

  total = sum(r['count'] for r in result)
  result = {"total": total, **{r['user_to__email']: {"count": r['count']} for r in result},"coins":a,"earned":b}

  return Response(result)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def asked_like(request):
  req = request.data
  username1 = req["username1"]
  username2 = req["username2"]
  question_id = req["question"]
  profile_qs = Profile.objects.filter(email__in=[username1, username2])
  profiles = {profile.email: profile for profile in profile_qs}
  question = AskQuestion.objects.select_related("group").get(id=question_id)
  members = Members.objects.filter(group=question.group)

  like = AskedLike.objects.create(
      user_from=profiles[username1],
      user_to=profiles[username2],
      question=question,
      group=question.group,
  )

  profiles[username2].total_likes = profiles[username2].total_likes + 1
  profiles[username2].save()

  likes = AskedLike.objects.filter(group=question.group, question=question)
  result = (
      likes.values('user_to__name',"user_to__email")
      .annotate(count=Count('id'))
      .values('user_to__name','count',"user_to__email")
      .order_by("-count")
  )
  
  a = profiles[username1].coins 
  b = 0
  if result[0]["user_to__email"] == username2:
    a = profiles[username1].coins + group.count
    b = group.count
    profiles[username1].coins = a
    profiles[username1].save()

  total = sum(r['count'] for r in result)
  result = {"total": total, **{r['user_to__name']: {"count": r['count']} for r in result},"coins":a,"earned":b}

  return Response(result)


from itertools import chain


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_likes_data(request):
  with transaction.atomic():
    user = Profile.objects.get(email = request.user.username)
    likes = Like.objects.filter(user_to=user).select_related('group', 'user_to',"user_from").order_by("-time")[:100]
    asked = AskedLike.objects.filter(user_to = user).select_related("group","user_to","question","user_from").order_by("-time")[:50]
  union = chain(likes,asked)
  serializer1 = LikeSerializer(union,many=True)

  with transaction.atomic():
    likes = Like.objects.filter(group__members__user=user).exclude(user_to = user).select_related('group', 'user_to',"user_from").order_by("-time")[:50]
    asked = AskedLike.objects.filter(group__members__user=user).exclude(user_to = user).select_related('group', 'user_to',"question","user_from").order_by("-time")[:50]
  union = chain(likes,asked)
  serializer2 = FriendLikeSerializer(union,many=True)

  return Response({"mine":serializer1.data,"friends":serializer2.data})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_visited(request):
  req = request.data

  if req["source"] == "ik":
    like = Like.objects.get(id = req["id"])
  else:
    like = AskedLike.objects.get(id = req["id"])

  like.visited = True
  like.save()

  return Response("Visited set True")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_reveal(request):
  like_id = request.data["like"]
  like = Like.objects.get(id = like_id)
  if like.user_from.mode == True:
    return Response("Premium")
  else:
    if like.revealed == False:
      user = Profile.objects.get(email = request.user.username)
      # user = Profile.objects.get(email = "9562267229")
      if user.coins >= 200:
        user.coins -= 200
        serializer = FromUserSerializer(like.user_from,many = False)
        user.save()
        like.revealed = True
        like.save()
      else:
        return Response("Insufficient coins")
    else:
      serializer = FromUserSerializer(like.user_from,many = False)
  return Response(serializer.data)
