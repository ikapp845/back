from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
import uuid
from user.models import Profile
from question.models import Question
import random
import string
from datetime import datetime


def key_generator():
    key = ''.join(random.choice(string.digits) for x in range(6))
    if Group.objects.filter(id=key).exists():
        key = key_generator()
    return key



class Group(models.Model):
  name = models.CharField(max_length = 200,null  =True,blank = True)
  id = models.CharField(max_length=6, default=key_generator, unique=True, editable=False,primary_key = True)




class Members(models.Model):
  id = models.UUIDField(default = uuid.uuid4,unique = True,primary_key = True,editable = False)
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  user = models.ForeignKey(Profile,on_delete = models.CASCADE)



class GroupQuestion(models.Model):
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  question = models.ForeignKey(Question,on_delete = models.CASCADE)
  time = models.DateTimeField(default = datetime.now(),null = True,blank = True)

  def __str__(self):
    return self.question.question + "  " + self.group.name

class Questionattended(models.Model):
  group = models.ForeignKey(Group,on_delete=models.CASCADE)
  question = models.ForeignKey(Question,on_delete = models.CASCADE)
  user = models.ForeignKey(Profile,on_delete = models.CASCADE)