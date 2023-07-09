from django.urls import path
from . import views


urlpatterns = [
  path("create_group/",views.create_group,name = "Create Group"),
  path("join_group/",views.join_group,name = "Join Group"),
  path("group_main/<str:group>/<str:email>/",views.group_main,name = "Group Question"),
  path("group_members/<str:group>",views.group_members,name = "Group Members"),
  path("leave/",views.leave,name = "Leave Group"),
  path("user_groups/<str:username>/",views.user_groups,name = "UserGroups"),
  path("add_question/",views.add_question,name = "Add Question"),
  path("add/",views.add,name = "asd"),
  path("report/<str:group>/<str:question>",views.report,name = "Report"),
  path("add_group_members/",views.add_group_members_contact,name = "Add members"),
  path("remove_member/",views.remove_member,name = "Remove members"),
  path("delete_account",views.delete_account,name = "Delete Account")
]