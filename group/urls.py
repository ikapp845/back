from django.urls import path
from . import views


urlpatterns = [
  path("create_group/",views.create_group,name = "Create Group"),
  path("join_group/",views.join_group,name = "Join Group"),
  path("group_question/<str:group>/<str:username>/",views.group_question,name = "Group Question"),
  path("group_members/<str:group>/",views.group_members,name = "Group Members"),
  path("leave/",views.leave,name = "Leave Group"),
  path("user_groups/<str:username>/",views.user_groups,name = "UserGroups")
]