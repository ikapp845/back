from django.db import models
from user.models import Profile
from group.models import Group,AskQuestion
from datetime import datetime
from django.utils import timezone


class Like(models.Model):
  id = models.AutoField(primary_key=True,editable=False,unique=True)
  user_from =  models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "fromuser")
  user_to = models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "touser")
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  question = models.IntegerField(default = 0,null=False)
  time = models.DateTimeField(default = timezone.now)
  visited = models.BooleanField(default = False,null = True,blank = True)
  source = models.CharField(default = "ik",max_length = 100)
  revealed = models.BooleanField(default=False)

  def __str__(self):
    return self.user_from.name + " to " + self.user_to.name


class AskedLike(models.Model):
  id = models.AutoField(primary_key=True,editable=False,unique=True)
  user_from =  models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "fromuserask")
  user_to = models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "touserask")
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  question = models.ForeignKey(AskQuestion, on_delete = models.CASCADE)
  time = models.DateTimeField(default = timezone.now,null = True,blank = True)
  visited = models.BooleanField(default = False)
  source = models.CharField(default = "user",max_length = 100)
  revealed = models.BooleanField(default=False)

  def __str__(self):
    return self.user_from.name + " to " + self.user_to.name + self.group.name + self.question.question




# Create your models here.
