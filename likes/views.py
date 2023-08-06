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
  question = req["question"]
  user_to, user_from = Profile.objects.filter(
      Q(email=username1) | Q(email=username2)
  ).order_by('email')

  if user_to.email == username1:
      user_to, user_from = user_from, user_to
  group = Group.objects.get(id = req["group"])
  print(user_to,user_from)
  like = Like.objects.create(
      user_from_id=username1,
      user_to_id=username2,
      question=question,
      group_id=req["group"],
  )

  result = (
      Like.objects.filter(group_id=req["group"], question=question)
      .values('user_to__name',"user_to__email")
      .annotate(count=Count('id'))
      .values('user_to__name','count',"user_to__email")
  )

  print(user_to.total_likes)
  user_to.total_likes = user_to.total_likes + 1
  print(user_to.total_likes)
  b = 0
  a = user_from.coins 
  if result[0]["user_to__email"] == username2:
    a = user_from.coins + group.count
    b = group.count
    user_from.coins = a
  Profile.objects.bulk_update([user_to,user_from],["coins","total_likes"])

  total = sum(r['count'] for r in result)
  result = {"total": total, **{r['user_to__email']: {"count": r['count']} for r in result},"coins":a,"earned":b}

  return Response(result)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def asked_like(request):
  req = request.data
  username1 = req["username1"]
  username2 = req["username2"]
  question_id = req["question"]
  user_to,user_from = Profile.objects.filter(email__in=[username1, username2])
  question = AskQuestion.objects.select_related("group").get(id=question_id)

  like = AskedLike.objects.create(
      user_from_id=username1,
      user_to_id=username2,
      question=question,
      group=question.group,
  )

  user_to.total_likes = user_to.total_likes + 1

  likes = AskedLike.objects.filter(group=question.group, question=question)
  result = (
      likes.values('user_to__name',"user_to__email")
      .annotate(count=Count('id'))
      .values('user_to__name','count',"user_to__email")
      .order_by("-count")
  )
  
  a = user_from.coins 
  b = 0
  if result[0]["user_to__email"] == username2:
    a = user_from.coins + group.count
    b = group.count
    user_from.coins = a
  Profile.objects.bulk_update([user_to,user_from],["coins","total_likes"])

  total = sum(r['count'] for r in result)
  result = {"total": total, **{r['user_to__name']: {"count": r['count']} for r in result},"coins":a,"earned":b}

  return Response(result)


from itertools import chain


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_likes_data(request):
  with transaction.atomic():
    likes = Like.objects.filter(user_to__email=request.user.username).select_related('group', 'user_to',"user_from").order_by("-time")[:100]
    asked = AskedLike.objects.filter(user_to__email = request.user.username).select_related("group","user_to","question","user_from").order_by("-time")[:50]
  union = chain(likes,asked)
  serializer1 = LikeSerializer(union,many=True)

  with transaction.atomic():
    likes = Like.objects.filter(group__members__user__email = request.user.username).exclude(user_to__email = request.user.username).select_related('group', 'user_to',"user_from").order_by("-time")[:50]
    asked = AskedLike.objects.filter(group__members__user__email = request.user.username).exclude(user_to__email = request.user.username).select_related('group', 'user_to',"question","user_from").order_by("-time")[:50]
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
