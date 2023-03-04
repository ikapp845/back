from django.db import models
import uuid
from user.models import Profile
from group.models import Group
from question.models import Question
from datetime import datetime

class Like(models.Model):
  id = models.UUIDField(default = uuid.uuid4,editable = False,primary_key = True)
  user_from =  models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "fromuser")
  user_to = models.ForeignKey(Profile,on_delete = models.CASCADE,related_name = "touser")
  group = models.ForeignKey(Group,on_delete = models.CASCADE)
  question = models.ForeignKey(Question,on_delete = models.CASCADE,null = True)
  time = models.DateTimeField(default = datetime.now(),null = True,blank = True)

  def __str__(self):
    return self.user_from.name + " to " + self.user_to.name




# Create your models here.
