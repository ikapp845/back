from django.shortcuts import render
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Profile
from group.models import Members,Group
from likes.models import Like,AskedLike
from group.serializers import ProfileSerializer
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from group.serializers import UserSerializer
from email.message import EmailMessage
import requests
import random
import string
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework_simplejwt import views as jwt_views
# Create your views here.





@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post(request):
  req = request.data
  user = User.objects.get(username = request.user.username)
  try:
    prof = Profile.objects.get(email = user.username)
    serializer = UserSerializer(prof,many = False)
    return Response(serializer.data)
  except:
    with transaction.atomic():
      try:
        profile = Profile.objects.create(email = user.username,user = user,gender = req["gender"],name = req["username"])
        profile.image_url = request.FILES["image"]
        profile.save()
      except:
        return Response("No user")
      serializer = UserSerializer(profile,many = False)
      return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_image(request):
  req = request.data
  with transaction.atomic():
    try:
      profile = Profile.objects.get(email = request.user.username)
      profile.image_url = request.FILES["image"]
      profile.save()
    except:
      return Response("error")
    serializer = UserSerializer(profile,many = False)
    return Response(serializer.data)


def key_generator():
    key = ''.join(random.choice(string.digits) for x in range(6))
    return key


import environ
env = environ.Env()
environ.Env.read_env()

@api_view(["GET"])
def check_username(request,email):
  otp = key_generator()
  try:
    name = User.objects.get(username = email)
    name.set_password(otp)
    name.save()
  except:
    new = User.objects.create_user(username = email,password= otp)
    new.save()
  result = requests.get(f"https://2factor.in/API/V1/5dc6d93d-bca5-11ed-81b6-0200cd936042/SMS/{email}/{otp}/ik")
  print(otp)
  return Response("otp sent")

@api_view(["GET"])
def check_otp(request,email,otp):
  response = requests.post("https://ik-l2n0.onrender.com/user/token/",data = {"username":email,"password":otp})
  if response:
    try:
      prof = Profile.objects.get(email = email)
      serializer = UserSerializer(prof,many = False)
      return Response({"data":serializer.data,"token":response.json()})
    except:
      return Response({"token":response.json()})
  else:
    return Response("Fail")
  return Response(response.json())


def clean_phone_number(number_str):
    # Remove "+91" and all spaces from the string
    digits_only = number_str.replace('+91', '').replace(' ', '')
    
    # Verify that the resulting string consists of exactly 10 digits
    if len(digits_only) == 10 and digits_only.isdigit():
        return digits_only
    else:
        return False
def edit_numbers(numbers):
    edited_numbers = []
    for number in numbers:
        number = number.replace(" ", "") # remove spaces
        if number.startswith("+91"): 
            number = number[3:] # remove +91
        if len(number) == 10 and number not in edited_numbers: # check length and duplication
            edited_numbers.append(number)
    return edited_numbers

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def check_email(request):
#   try:
#     user = Profile.objects.get(email = request.user.username)
#     serializer = UserSerializer(user,many= False)
#     return Response(serializer.data)
#   except:
#     return Response("no user")

import codecs

@api_view(["POST"])
def get_contacts(request):
  contacts = request.data["contacts"]

  contacts = json.loads(contacts)

  contacts_edited = edit_numbers(contacts)
  users_found = Profile.objects.filter(email__in = contacts_edited)
  final = []
  for items in users_found:
    image_url = items.image_url.url if items.image_url else None
    final.append({"name":items.name,"id":items.email,"image":image_url})
  return Response(final)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_group_contacts(request):
  contacts = request.data["contacts"]
  group = request.data["group"]
  contacts = json.loads(contacts)

  contacts_edited = edit_numbers(contacts)
  users_found = Profile.objects.filter(email__in = contacts_edited)

  final = []
  members = Members.objects.values_list("user").filter(user__in = users_found,group = Group.objects.get(id= group))
  mem_set = set()
  for items in members:
    mem_set.add(items[0])

  for items in users_found:
    if items.email not in mem_set:
      final.append({"name":items.name,"id":items.email,"image":"https://profilepicik.s3.amazonaws.com/media/{}.jpg".format(items.email)})
  return Response(final)



from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token(request):

  user = Profile.objects.get(email = request.user.username)
  time = user.last_login
  user.last_login = timezone.now()
  user.save()

  a = False

  likes = Like.objects.filter(user_to=user).order_by("-time")
  if(likes):
    if likes[0].time >= time:
      a = True

  asked_likes = AskedLike.objects.filter(user_to=user).order_by("-time")
  if asked_likes:
    if asked_likes[0].time >= time:
      a = True

  return Response({'detail': 'Token is valid',"like":a})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_coins(request):
  user = Profile.objects.get(email = request.user.username)
  return Response({"user":user.email,"coins":user.coins})



