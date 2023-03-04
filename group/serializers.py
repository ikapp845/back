from rest_framework import serializers
from .models import GroupQuestion,Members,Group
from question.models import Question
from user.models import Profile
from likes.models import Like
import pytz

class GroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = Group
    fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
  groups = serializers.SerializerMethodField("get_groups")
  last_like = serializers.SerializerMethodField("get_last_like")

  class Meta:
    model = Profile
    fields = "__all__"

  def groups(self,profile):
    groups = Members.object.filter(user = profile)
    serializer = GroupSerializer(groups,many = True)
    return serializer.data

  def get_last_like(self,profile):
    login_time = profile.last_login
    login_time = login_time.replace(tzinfo=pytz.utc)
    try:
      likes = Like.objects.filter(user_to = profile).order_by("time")
      if likes[0].time > login_time:
        return True
      else:
        return False
    except:
      return ""


class QuestionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Question
    fields = ["question"]


class GroupQuestionSerializer(serializers.ModelSerializer):
  q = serializers.SerializerMethodField("get_question")

  class Meta:
    model = GroupQuestion
    fields = ["q"]

  def get_question(self,groupquestion):
    qu = groupquestion.question
    serializer = QuestionSerializer(qu,many = False)
    return serializer.data

class MemberSerializer(serializers.ModelSerializer):
  user = serializers.SerializerMethodField("get_users")

  class Meta:
    model = Members
    fields = ["user"]

  def get_users(self,member):
    user = member.user
    serializer = ProfileSerializer(user,many = False)
    return serializer.data
    

class UserGroupsSerializer(serializers.ModelSerializer):
  group = serializers.SerializerMethodField("get_groups")
  class Meta:
    model = Members
    fields = ["group"]

  def get_groups(self,member):
    group = member.group
    serializer = GroupSerializer(group,many = False)
    return serializer.data