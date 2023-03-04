from django.urls import path
from . import views


urlpatterns = [
  path("",views.like,name = "Like"),
  path("likes/<str:username>/",views.get_likes,name = "Get Likes"),
  path("like_count/<str:group>/<str:question>/",views.get_like_count,name = "Like count")
]