from django.db import models
import uuid
from user.models import Profile
from question.models import Question
import random
import string
from datetime import datetime
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.signals import (post_save,pre_delete)
from django.dispatch import receiver
from django_ulid.models import default,ULIDField

def key_generator():
     # Generate a list of possible characters
    characters = string.ascii_letters + string.digits
    
    # Use a list comprehension to randomly select 6 characters from the list
    code = ''.join(random.choice(characters) for i in range(6))
    # key = ''.join(random.choice(string.digits) for x in range(6))
    if Group.objects.filter(id=code).exists():
        code = key_generator()
    return code
    

class Group(models.Model):
  name = models.CharField(max_length = 200,null  =True,blank = True)
  id = models.CharField(max_length=6, default=key_generator, unique=True, editable=False,primary_key = True)
  admin = models.ForeignKey(Profile,on_delete = models.SET_NULL,null = True,blank = True)
  count = models.IntegerField(default = 0)

  def __str__(self):
    return self.name + " " + self.id


class Members(models.Model):
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  user = models.ForeignKey(Profile,on_delete = models.CASCADE)
  added = models.DateTimeField(default=timezone.now)

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user', 'group'], name='unique_user_group')
    ]


  def __str__(self):
    return self.group.name + "  " + self.user.name 

@receiver(post_save,sender =Members)
def member_added(sender,instance,created,*args,**kwargs):
  if created == True:
    group = instance.group
    group.count += 1
    group.save()

@receiver(pre_delete,sender = Members)
def member_deleted(sender,instance,*args,**kwargs):
  group = instance.group
  group.count -= 1
  group.save()

class GroupQuestion(models.Model):
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  question = models.CharField(max_length = 100,null = True,blank= True)
  question_id = models.CharField(max_length = 100,null = True,blank = True)
  time = models.DateTimeField(default = timezone.now)
  source = models.CharField(max_length = 100,null = True,blank = True)

  def __str__(self):
    return self.question + "  " + self.group.name



class AskQuestion(models.Model):
  id = ULIDField(default=default, primary_key=True, editable=False)
  group = models.ForeignKey(Group, on_delete = models.CASCADE)
  question = models.CharField(max_length = 200,null = True,blank = True)
  user = models.ForeignKey(Profile,on_delete = models.CASCADE,null = True,blank = True)
  time = models.DateTimeField(default=timezone.now)

  class Meta:
    indexes = [
      models.Index(fields = ["group"])
    ]



class Report(models.Model):
  id = models.UUIDField(default = uuid.uuid4,unique = True,primary_key = True,editable = False)
  group = models.ForeignKey(Group, on_delete = models.CASCADE,null = True,blank = True)
  question = models.ForeignKey(AskQuestion, on_delete = models.CASCADE,null = True,blank = True)
  