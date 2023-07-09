
from django.db import models
import uuid
# Create your models here.
class Question(models.Model):
  id = models.UUIDField(default = uuid.uuid4,editable = False,primary_key = True,unique = True)
  question = models.TextField(null = True,blank = True)

  def __str__(self):
    return self.question + " " + str(self.id)