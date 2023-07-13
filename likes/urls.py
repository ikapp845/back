from django.urls import path
from . import views


urlpatterns = [
  path("",views.like,name = "Like"),
  path("asked/",views.asked_like,name = "Asked Like"),
  path("all_likes/",views.get_likes_data,name = "All Likes data"),
  path("set_visited/",views.like_visited,name = "Visited Like"),
  path("reveal/",views.get_reveal,name = "Reveal")
]