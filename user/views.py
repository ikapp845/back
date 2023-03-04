from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Profile
from group.serializers import ProfileSerializer
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from group.serializers import UserSerializer
import ssl
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
# Create your views here.

class UserDataUpload(APIView):
  pasrser_classes = [MultiPartParser,FormParser]

  def post(self,request):
    
    req = request.data
    with transaction.atomic():
      profile = Profile.objects.get(email = req["email"])
      profile.name = req["username"]
      profile.gender = req["gender"]
      profile.password = req["password"]
      profile.image_url = req["image"]
      profile.save()
    serializer = UserSerializer(profile,many = False)
    return Response(serializer.data)

@api_view(["POST"])
def post(request):
  req = request.data
  with transaction.atomic():

    profile = Profile.objects.get(email = req["email"])
    profile.name = req["username"]
    profile.gender = req["gender"]
    profile.password = req["password"]
    profile.save()
    serializer = UserSerializer(profile,many = False)
    return Response(serializer.data)

def send_email(email,otp):    
  email_sender = str(os.getenv("email_sender"))
  email_password = str(os.getenv("email_password"))
  email_to = email

  subject = "OTP"
  body = otp

  em = EmailMessage()
  em["From"] = email_sender
  em["To"] = email_to
  em["Subject"] = subject
  em.set_content(body)

  context = ssl.create_default_context()

  with smtplib.SMTP_SSL("smtp.gmail.com",465,context = context) as smtp:
      smtp.login(email_sender,email_password)
      smtp.sendmail(email_sender,email_to,em.as_string())

# def key_generator():
#     key = ''.join(random.choice(string.digits) for x in range(6))
#     if Group.objects.filter(id=key).exists():
#         key = key_generator()
#     return key

@api_view(["GET"])
def check_username(request,email):
  
  try:
    name = Profile.objects.get(email = email)
    return Response("Fail")
  except:  

    new = Profile.objects.create(email = email)
    otp = new.otp
    send_email(email, otp)
    return Response("Success")

@api_view(["POST"])
def check_otp(request):
  req = request.data

  user = Profile.objects.get(email = req["email"])
  if req["otp"] == user.otp:
    return Response("Success")
  else:
    return Response("Fail")

@api_view(["POST"])
def verify(request,email):
  user = Profile.objects.get(email = email)
  if request.data.get("password",None) == user.password:
    serializer = UserSerializer(user,many = False)
    return Response(serializer.data)
  else:
    return Response("Fail")
# @api_view(['POST'])
# def otp_check(request):

    
@api_view(["GET"])
def delete_account(request,username):
  user = Profile.objects.get(email = username)
  user.delete()
  return Respone("delete")

@api_view(["GET"])
def check_email(request,mail):
  try:
    user = Profile.objects.get(email = mail)
    serializer = UserSerializer(user,many= False)
    return Response(serializer.data)
  except:
    return Response("no user")

@api_view(["GET"])
def login(request,mail):
  user = Profile.objects.get(email = mail)
  serializer = ProfileSerializer(user,many = False)
  return Response(serializer.data)


    


  