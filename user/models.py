from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
import random
import string
from django.contrib.auth.models import User
from django.utils import timezone



def key_generator():
    key = ''.join(random.choice(string.digits) for x in range(6))
    return key
    
class Profile(models.Model):
  user = models.ForeignKey(User, on_delete = models.CASCADE,null = True,blank = True)
  name = models.CharField(max_length = 200,null = True,blank = True)
  email = models.CharField(max_length = 200,primary_key=True,unique = True,editable=False)
  gender = models.CharField(max_length = 200,null = True,blank = True)
  last_login = models.DateTimeField(default=timezone.now,null = True,blank = True)
  image_url = models.ImageField(upload_to = "media/",null = True,blank = True)
  total_likes = models.IntegerField(null = True,blank = True,default=0)
  coins = models.IntegerField(default = 0)
  mode = models.BooleanField(default = False)

  def __str__(self):
    return self.email

# Create your models here.
