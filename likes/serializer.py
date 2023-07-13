from rest_framework import serializers
from .models import Like
from group.serializers import ProfileSerializer
from user.models import Profile
from questions import questions



class LikeSerializer(serializers.ModelSerializer):
  question = serializers.SerializerMethodField("get_question")
  from_gender = serializers.SerializerMethodField("get_fromgender")
  username = serializers.SerializerMethodField("to_username")

  class Meta:
    model = Like
    exclude = ["user_from","user_to","group"]


  def get_question(self,like):
    if like.source == "ik":
      id = like.question
      return questions[id]["question"]
    else:
      return like.question.question


  def to_username(self,like):
    return like.user_to.name

  def get_fromgender(self,like):
    return like.user_from.gender
 
 
class FriendLikeSerializer(serializers.ModelSerializer):
  question = serializers.SerializerMethodField("get_question")
  from_gender = serializers.SerializerMethodField("get_fromgender")
  username = serializers.SerializerMethodField("to_username")
  viewed = serializers.SerializerMethodField("to_viewed")

  class Meta:
    model = Like
    exclude = ["user_from","user_to","group","source","visited"]

  def to_viewed(self,like):
    return False

  def get_question(self,like):
    return like.question.question


  def to_username(self,like):
    return like.user_to.name

  def get_fromgender(self,like):
    return like.user_from.gender


class FromUserSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Profile
    exclude = ["coins","user","last_login","total_likes","gender"]

  