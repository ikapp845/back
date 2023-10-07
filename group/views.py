from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Group,Members,AskQuestion,GroupQuestion
from django.shortcuts import render
from user.models import Profile
from .serializers import GroupQuestionSerializer,MemberSerializer,GroupQuestionSerializer
from datetime import datetime
from django.utils.timezone import localtime 
from .serializers import UserGroupsSerializer
from django.utils import timezone
from .models import AskQuestion,Report
import json
from django.core.cache import cache
from django.contrib.auth.models import User
from questions import questions
import random
from question.models import Question


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):
  with transaction.atomic():
    req = request.data
    group = Group.objects.create(name= req["name"],admin_id = request.user.username)
    group.save()

    
    member = Members.objects.create(group = group,user_id = request.user.username)
    member.save()

  return Response(group.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
  req = request.data

  try:
    member = Members.objects.get(group_id = req["group"],user_id= request.user.username)
    return Response("User already in group")
  except:
    try:
      member = Members.objects.create(group_id = req["group"],user_id = request.user.username)
      return Response("Success")
    except:
      return Response("Group does not exist")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_group_members_contact(request):
    with transaction.atomic():
        contacts = request.data["selected"]
        group = Group.objects.get(id=request.data["group"])
        members = [Members(group_id = request.data["group"], user_id = user) for user in contacts]
        l = len(members)
        group.count += l
        group.save()
        Members.objects.bulk_create(members)
    return Response("Added")


def compare_dates(desired,now):
  if desired.year == now.year:
    if desired.month == now.month:
      if desired.day == now.day:
        if (now.hour - desired.hour) >= 1:
          return True
        else:
          return False
      else:
        return True
    else:
      return True
  else:
    return True


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_members(request,group):
  members = Members.objects.select_related("user","group").filter(group_id = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_main(request,group,email):

  def group_members(gp):
    members = Members.objects.select_related("user","group").filter(group_id = gp)
    serializer = MemberSerializer(members,many = True)
    return serializer.data

  def group_questions(group):
    question_list = GroupQuestion.objects.filter(group_id = group)
    now = timezone.now()
    before = now - timezone.timedelta(hours = 1)
    if not question_list or compare_dates(question_list[len(question_list) - 1].time, now) == True:
      if question_list:
        before = question_list[0].time 
        question_list.delete()
      user_que = AskQuestion.objects.filter(group_id = group,time__gt = before)[:10]
      user_que_count = len(user_que)
      res = random.sample(list(questions.values()),10-user_que_count)
      question_list = list(user_que) + list(res)
      a = []
      for items in question_list:
        question = GroupQuestion()
        question.question_id = items['id']
        question.question = items['question']
        question.source = 'user' if isinstance(items, AskQuestion) else 'ik'
        question.group_id = group
        a.append(question)
      group_question = GroupQuestion.objects.bulk_create(a,10)
      question_list = group_question
      time = question_list[0].time
    else:
      time = question_list[0].time
    serializer = GroupQuestionSerializer(question_list,many = True)
    return serializer.data,str(time)
    


  group_mem  = group_members(group)
  group_ques,time= group_questions(group)
  final = {"members":group_mem,"questions":group_ques,"time" : time}
  return Response(final)

 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave(request):
  req = request.data
  with transaction.atomic():
    group = Group.objects.get(id =req["group"] )
    user = Profile.objects.get(email= request.user.username)
    if group.admin == user:
      try:
        new_admin = Members.objects.filter(group = items).order_by("added")[1]
        items.admin = new_admin.user
        items.save()
      except IndexError:
        items.delete()
    mem = Members.objects.get(group = group,user = user)
    mem.delete()
  return Response("removed")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_groups(request,username):
  members = Members.objects.select_related("group","user").filter(user_id = username).defer("added")
  serializer = UserGroupsSerializer(members,many  = True)
  return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_question(request):
  req = request.data
  group = Group.objects.get(id = req["group"])
  question = AskQuestion.objects.create(group = group,question = req["question"],user = Profile.objects.get(email = request.user.username))
  question.save()
  return Response("Question Added")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report(request,group,question):
  group = Group.objects.get(id = group)
  question = AskQuestion.objects.get(id = question)
  report = Report.objects.create(group = group,question = question)
  report.save()
  return Response("Reported")

from django.core.cache import cache

@api_view(["GET"])
def add(request):
  q = [
    "Has the best outfits👕👚",
    "Always on phone📱",
    "Has the cutest smile 😊",
    "Should be a food vlogger 🍔",
    "A homie you never want to lose ❤",
    "Likely to be a millionaire in future 💸",
    "Would be late for their own wedding 🤵👰‍♀",
    "Will become a reality tv star 🕺",
    "Would get a lot of tattoos in future ☮",
    "likely to become a social media influencer 🤳",
    "Spends all weekend binging a new tv series",
    "Most likely to live the longest out of all friends",
    "Would adopt a #vanlife lifestyle in future",
    "Would be the first to get married",
    "Would accidentally find a portal to another dimension",
    "Cries a lot while watching a sad movie",
    "Would get rid of their smartphone and go back to using a flip phone",
    "Most likely to have visited the largest number of countries in future",
    "Who is most likely to move to a foreign country",
    "Would show up on your doorstep with soup when you're sick",
    "Would become a stand-up comedian in future",
    "Likely to die first in a scary movie",
    "Would become a teacher at their high school",
    "Knows about new restaurants before everyone else",
    "Always have the best snacks",
    "Make new friends whenever they're out",
    "Texts 'on my way' when they're still getting ready",
    "Always forget to text back",
    "Forgets even their best friends birthday",
    "Would eat something off the ground",
    "Spends all their money on stupid things",
    "Most likely to marry a celebrity in future",
    "Would win the Nobel prize",
    "Should become our prime minister",
    "Likely to give their kid an unusual (terrible) name",
    "Is late for everything",
    "Spends hours watching conspiracy theories in YouTube",
    "Get lost in their own hometown",
    "Should have a reality show of their own",
    "Would marry someone they just met",
    "Takes a whole week to reply to a text",
    "Cut their own hair (and think it looks good)",
    "Asks for advice but never takes it",
    "Always cancel plans at the last moment",
    "Laughs in a serious moment",
    "Save up all their money and never spend it",
    "Most likely to be killed first if they were in a horror movie",
    "Would answer the phone if you call in the middle of a night",
    "Treats your house like their house",
    "Get along better with your parents than you do",
    "Tries to embarrass you in front of your crush",
    "Makes you laugh when you are sad",
    "Takes care of you when you are sick",
    "Gives the best nickname to everyone",
    "Would scream in the middle of a horror movie",
    "Most likely to cheat at a board game",
    "a role model for the group",
    "Always take the time to listen",
    "Always show up for moral support",
    "Picks out the perfect present for anybody",
    "Would write a bestselling book in future",
    "The person you would call after a breakup",
    "Would say something stupid on their first date",
    "name would be written  in future history books📚",
    "is most likely to eat pizza for breakfast🍕",
    "Should become a politician 🗣",
    "Should dj every party 🤘",
    "to have the most children 👶🏻",
    "Who is most likely to become a CEO at a top company 👨‍💼👩‍💼",
    "Would join the army and save nation 🪖",
    "Who do you secretly admire",
    "would get lost on a trip ✈",
    "Probably will grow to 7 feet tall 🕴",
    "Always drrssed to impress 👌",
    "Spends all money on clothes 👕",
    "a autoenthusiast 🏎🏍",
    "likely to fall asleep during a meeting 😴",
    "likely to forget to turn off the mic during a Zoom call 😂",
    "Who will become a professional footballer ⚽",
    "Would answer the phone even if you call in the middle of a night 🙋‍♂",
    "Get along better with your parents than you do 🫤",
    "Most likely to accidentally wear the same outfit as you 🫂",
    "Forgets to mute the microphone during Zoom calls 🤫",
    "Talks in the theater during a movie 💬",
    "Screams in the middle of a horror movie 😱",
    "Makes you forget your problems 🫂",
    "Always falls asleep in class 💤",
    "get hungry in the middle of the night 🍲",
    "Panics about failing and then  gets full mark 💯",
    "remains asleep while the alarm is blaring ⏰",
    "Wait until the last minute to do a project and still get an A 😎",
    "Would give their kid a pretty terrible name 😬",
    "Snooze alarm indefinitely in the mornings ⏰",
    "Most likely to cheat on a test and get caught",
    "replace salt with sugar while cooking 😹",
    "Clicks on every spam ad pop-up on the internet",
    "Tell jokes that gets them into trouble",
    "sleep while brushing their teeth 💤",
    "popular at school 😎",
    "Promise they'll study but stays up all night scrolling on phone",
    "have the best insta profile picture 🖼",
    "days 🤒",
    "pick up your calls in the middle of the night 📲",
    "send instagram reels everyday  🙂",
    "Who is most likely to text back immediately 💬",
    "to be a cool parent 👨‍👩‍👧‍👦",
    "have the best dance moves at a party   💃🕺",
    "gets you the best birthday gift",
    "Who is most likely to plan the future",
    "takes longer to get ready in the morning 😅",
    "more romantic 💗",
    "remind the teacher about homework 🥲",
    " Who is the biggest film enthusiast you know 🎬",
    " most likely to be the first to get a car 🚘🔥",
    " Who would most likely sleepwalk 😴🚶🏻‍♂",
    " Chooses classical music over hip hop 🎶",
    " Who will most likely make it big as an actor or actress 🤷🏻‍♂🤷🏻‍♀",
    " Anime enthusiast in group 🧛🏻‍♂🥷🏾",
    " Gets angry over anything👿😡",
    " The entire squads lawyer, always ready to throw hands👊🏼",
    " I have never seen them angry😉✨",
    " Captures every life event on snap but never posts 🤳🏼",
    "Always has less than 10% battery 🔋",
    "Always knows what's going on in the world 🌏",
    "Says their single but is dating secretly 🫣",
    "Best glow up i ever seen ✨",
    "Wins every video game, every time 🎮",
    "They crashed into your life and changed everything 💫",
    "Has the most followers on Instagram 🔥",
    "Want to steal them from their bf/gf",
    "The most beautiful person you have ever met 💕",
    "Next Olympic medalist 🥇",
    "Is an expert in faking their father's signature✒",
    "Tells un funniest jokes and laughs themselves 😑",
    "Most likely to write a Netflix series 🎬",
    "Wouldn't be surprised if they drop their phone in the toilet 🚽",
    "Knows the subject more than the teacher 👩‍🏫",
    "The one to finish the group project the morning it's due ⏰",
    "Has the best ringtone 🎶",
    "Always know what to say and when to say 🫡",
    "Their diary would be a movie script 🎬",
    "Would watch cartoons even in their 60s",
    "Cries over the silliest things possible 😫🤦‍♂",
    "Still stalks their ex online 👀",
    "They are peanut butter to my jam🥪",
    "They deserve a national holiday in their honour🏅",
    "They're always positive about anything😇",
    "You deserve a vacation, you've been working so hard 🏖",
    "Most likely to offer to carry your uncomfortable shoes👠",
    "Most likely to offer to carry your uncomfortable shoes👠",
    "The organiser of every friend-get-together 🫂",
    "You'd walk through fire for them🫳",
    "Knows everyone🥰",
    "Always shows up in times of need 💪",
    " Have never seen them in class 😂",
    "Knows just how to make every teacher mad🤣",
    "Mom/Dad of the group (and so loved for it)",
    "Life of the party🥳",
    "Always keep their promises no matter what 🤝",
    " Alexa play 'dandelions', I think I'm in love ♥🎼",
    "Lives life like a party 🥳",
    " I will fight anyone for you 👊🏼",
    "Makes everybody feel like they belong😌",
    "Best to convince your parents to let you go out 🤩",
    "Can cook anything in the microwave😅",
    "Wanna take them wherever I go 🌎",
    " The organiser of every get together 🏞🌅",
    "My family that i chose 🥰",
    "Would become famous for something weird 🥴",
    "Could start dancing in the middle of a public place 🕺",
    "Stares at their own photo for hours 🤦‍♂",
    "Is listening to BTS right about now 💜",
    "Every teacher loves them ☺",
    "Always in fight with friends 😤",
    " Guess who's my fav person 🌝❤",
    "Can talk to anybody they just met for hours 🗣",
    "Cancels trip at the last minute 🤦‍♂",
    "Future fashion designer 👜",
    " Animal lover 🦬🐅",
    " First person to complete the rubics cube",
    "Has best hairstyle💇‍♂💇",
    "Could recognise their voice anywhere🙉",
    "Sings karaoke like a pro🎤",
    "As cool as friggin cucumber🥒",
    "Could convince anyone of a lie 😜",
    " Most likely to check up on you after you reach home late 🥺",
    " Looked crisp as f on the first day of school/collage 😼",
    "Draw portraits of strangers in public spaces 🎨",
    " Kicking my feet in the air when I see their text 🦥",
    " Look like they belong to the kardashian clan 🤭",
    " Life without them is like eating soup with a fork 😒",
    " Jokes are funnier when they tell them 😆",
    " Would make them a spotify playlist 😁❤",
    " Knows the weirdest facts 🧐",
    " Let's meet up this weekend 🤔",
    " sleep thru math class 📐",
    " Has made 'wearing crocs' Their entire personality 🌝",
    "Could pull off any colour 🧑‍🦰",
    "Dances like no one 💃",
    "Make u feel valued💎",
    "Crazy about them since primary school👹",
    "Look up 'gorgeous' in the dictionary and find their photo😍",
    "Get jealous so easily 🤭",
    "I love seeing them making babies smile👶🏻",
    "Has the best outfits👕👚",
    "Always on phone📱",
    "Has the cutest smile 😊",
    "Should be a food vlogger 🍔",
    "A homie you never want to lose ❤",
    "Likely to be a millionaire in future 💸",
    "Would be late for their own wedding 🤵👰‍♀",
    "Will become a reality tv star 🕺",
    "Would get a lot of tattoos in future ☮",
    "likely to become a social media influencer 🤳",
    "Spends all weekend binging a new tv series",
    "Most likely to live the longest out of all friends",
    "Would adopt a #vanlife lifestyle in future",
    "Would be the first to get married",
    "Would accidentally find a portal to another dimension",
    "Cries a lot while watching a sad movie",
    "Would get rid of their smartphone and go back to using a flip phone",
    "Most likely to have visited the largest number of countries in future",
    "Who is most likely to move to a foreign country",
    "Would show up on your doorstep with soup when you're sick",
    "Would become a stand-up comedian in future",
    "Likely to die first in a scary movie",
    "Would become a teacher at their high school",
    "Knows about new restaurants before everyone else",
    "Always have the best snacks",
    "Make new friends whenever they're out",
    "Texts 'on my way' when they're still getting ready",
    "Always forget to text back",
    "Forgets even their best friends birthday",
    "Would eat something off the ground",
    "Spends all their money on stupid things",
    "Most likely to marry a celebrity in future",
    "Would win the Nobel prize",
    "Should become our prime minister",
    "Likely to give their kid an unusual (terrible) name",
    "Is late for everything",
    "Spends hours watching conspiracy theories in YouTube",
    "Get lost in their own hometown",
    "Should have a reality show of their own",
    "Would marry someone they just met",
    "Takes a whole week to reply to a text",
    "Cut their own hair (and think it looks good)",
    "Asks for advice but never takes it",
    "Always cancel plans at the last moment",
    "Laughs in a serious moment",
    "Save up all their money and never spend it",
    "Most likely to be killed first if they were in a horror movie",
    "Would answer the phone if you call in the middle of a night",
    "Treats your house like their house",
    "Get along better with your parents than you do",
    "Tries to embarrass you in front of your crush",
    "Makes you laugh when you are sad",
    "Takes care of you when you are sick",
    "Gives the best nickname to everyone",
    "Would scream in the middle of a horror movie",
    "Most likely to cheat at a board game",
    "a role model for the group",
    "Always take the time to listen",
    "Always show up for moral support",
    "Picks out the perfect present for anybody",
    "Would write a bestselling book in future",
    "The person you would call after a breakup",
    "Would say something stupid on their first date",
    "name would be written  in future history books📚",
    "is most likely to eat pizza for breakfast🍕",
    "Should become a politician 🗣",
    "Should dj every party 🤘",
    "to have the most children 👶🏻",
    "Who is most likely to become a CEO at a top company 👨‍💼👩‍💼",
    "Would join the army and save nation 🪖",
    "Who do you secretly admire",
    "would get lost on a trip ✈",
    "Probably will grow to 7 feet tall 🕴",
    "Always drrssed to impress 👌",
    "Spends all money on clothes 👕",
    "a autoenthusiast 🏎🏍",
    "likely to fall asleep during a meeting 😴",
    "likely to forget to turn off the mic during a Zoom call 😂",
    "Who will become a professional footballer ⚽",
    "Would answer the phone even if you call in the middle of a night 🙋‍♂",
    "Get along better with your parents than you do 🫤",
    "Most likely to accidentally wear the same outfit as you 🫂",
    "Forgets to mute the microphone during Zoom calls 🤫",
    "Talks in the theater during a movie 💬",
    "Screams in the middle of a horror movie 😱",
    "Makes you forget your problems 🫂",
    "Always falls asleep in class 💤",
    "get hungry in the middle of the night 🍲",
    "Panics about failing and then  gets full mark 💯",
    "remains asleep while the alarm is blaring ⏰",
    "Wait until the last minute to do a project and still get an A 😎",
    "Would give their kid a pretty terrible name 😬",
    "Snooze alarm indefinitely in the mornings ⏰",
    "Most likely to cheat on a test and get caught",
    "replace salt with sugar while cooking 😹",
    "Clicks on every spam ad pop-up on the internet",
    "Tell jokes that gets them into trouble",
    "sleep while brushing their teeth 💤",
    "popular at school 😎",
    "Promise they'll study but stays up all night scrolling on phone",
    "have the best insta profile picture 🖼",
    "days 🤒",
    "pick up your calls in the middle of the night 📲",
    "send instagram reels everyday  🙂",
    "Who is most likely to text back immediately 💬",
    "to be a cool parent 👨‍👩‍👧‍👦",
    "have the best dance moves at a party   💃🕺",
    "gets you the best birthday gift",
    "Who is most likely to plan the future",
    "takes longer to get ready in the morning 😅",
    "more romantic 💗",
    "remind the teacher about homework 🥲",
    " Who is the biggest film enthusiast you know 🎬",
    " most likely to be the first to get a car 🚘🔥",
    " Who would most likely sleepwalk 😴🚶🏻‍♂",
    " Chooses classical music over hip hop 🎶",
    " Who will most likely make it big as an actor or actress 🤷🏻‍♂🤷🏻‍♀",
    " Anime enthusiast in group 🧛🏻‍♂🥷🏾",
    " Gets angry over anything👿😡",
    " The entire squads lawyer, always ready to throw hands👊🏼",
    " I have never seen them angry😉✨",
    " Captures every life event on snap but never posts 🤳🏼",
    "Always has less than 10% battery 🔋",
    "Always knows what's going on in the world 🌏",
    "Says their single but is dating secretly 🫣",
    "Best glow up i ever seen ✨",
    "Wins every video game, every time 🎮",
    "They crashed into your life and changed everything 💫",
    "Has the most followers on Instagram 🔥",
    "Want to steal them from their bf/gf",
    "The most beautiful person you have ever met 💕",
    "Next Olympic medalist 🥇",
    "Is an expert in faking their father's signature✒",
    "Tells un funniest jokes and laughs themselves 😑",
    "Most likely to write a Netflix series 🎬",
    "Wouldn't be surprised if they drop their phone in the toilet 🚽",
    "Knows the subject more than the teacher 👩‍🏫",
    "The one to finish the group project the morning it's due ⏰",
    "Has the best ringtone 🎶",
    "Always know what to say and when to say 🫡",
    "Their diary would be a movie script 🎬",
    "Would watch cartoons even in their 60s",
    "Cries over the silliest things possible 😫🤦‍♂",
    "Still stalks their ex online 👀",
    "They are peanut butter to my jam🥪",
    "They deserve a national holiday in their honour🏅",
    "They're always positive about anything😇",
    "You deserve a vacation, you've been working so hard 🏖",
    "Most likely to offer to carry your uncomfortable shoes👠",
    "Most likely to offer to carry your uncomfortable shoes👠",
    "The organiser of every friend-get-together 🫂",
    "You'd walk through fire for them🫳",
    "Knows everyone🥰",
    "Always shows up in times of need 💪",
    " Have never seen them in class 😂",
    "Knows just how to make every teacher mad🤣",
    "Mom/Dad of the group (and so loved for it)",
    "Life of the party🥳",
    "Always keep their promises no matter what 🤝",
    " Alexa play 'dandelions', I think I'm in love ♥🎼",
    "Lives life like a party 🥳",
    " I will fight anyone for you 👊🏼",
    "Makes everybody feel like they belong😌",
    "Best to convince your parents to let you go out 🤩",
    "Can cook anything in the microwave😅",
    "Wanna take them wherever I go 🌎",
    " The organiser of every get together 🏞🌅",
    "My family that i chose 🥰",
    "Would become famous for something weird 🥴",
    "Could start dancing in the middle of a public place 🕺",
    "Stares at their own photo for hours 🤦‍♂",
    "Is listening to BTS right about now 💜",
    "Every teacher loves them ☺",
    "Always in fight with friends 😤",
    " Guess who's my fav person 🌝❤",
    "Can talk to anybody they just met for hours 🗣",
    "Cancels trip at the last minute 🤦‍♂",
    "Future fashion designer 👜",
    " Animal lover 🦬🐅",
    " First person to complete the rubics cube",
    "Has best hairstyle💇‍♂💇",
    "Could recognise their voice anywhere🙉",
    "Sings karaoke like a pro🎤",
    "As cool as friggin cucumber🥒",
    "Could convince anyone of a lie 😜",
    " Most likely to check up on you after you reach home late 🥺",
    " Looked crisp as f on the first day of school/collage 😼",
    "Draw portraits of strangers in public spaces 🎨",
    " Kicking my feet in the air when I see their text 🦥",
    " Look like they belong to the kardashian clan 🤭",
    " Life without them is like eating soup with a fork 😒",
    " Jokes are funnier when they tell them 😆",
    " Would make them a spotify playlist 😁❤",
    " Knows the weirdest facts 🧐",
    " Let's meet up this weekend 🤔",
    " sleep thru math class 📐",
    " Has made 'wearing crocs' Their entire personality 🌝",
    "Could pull off any colour 🧑‍🦰",
    "Dances like no one 💃",
    "Make u feel valued💎",
    "Crazy about them since primary school👹",
    "Look up 'gorgeous' in the dictionary and find their photo😍",
    "Get jealous so easily 🤭",
    "I love seeing them making babies smile👶🏻",
    " There's something wrong with my phone, could you try putting your number in it 🌝",
    "Can't handle pressure 😮‍💨",
    "I would get their name tattooed 〰",
    "Has multiple love languages 💕",
    "I will treat you better than your current bf/gf ❣",
    "They always see the best in people 😊",
    "CEO of making weird faces while taking selfies 😙",
    "Remind me to bring an oxygen cylinder the next time we meet 😶‍🌫",
    "Ghosts people all the time 👻",
    "The milk to my fruit loops 🍒",
    "Would download duolingo but never use it 😅",
    "Their pet hates me for no reason 😭",
    "Knows how to turn every obstacle into opportunity 💪",
    "Rocks their piercings 🤟🏽",
    "Never wants to grow up 👼",
    "The micro influencer of our town 🤳🏼",
    "Turns into hulk when their friend is in trouble 💪🏼",
    "They are super lucky for me 🍃",
    "Iam too shy around them 😳🫣",
    "They never sleep but somehow always have energy⚡",
    "I'd thank them first in my oscar acceptance speech 🏆",
    "They've impacted my life in ways they dont even know 😓",
    " Can't believe a word that comes out of their mouth 🤣",
    " Need constant reassurance that their friends are not sick of them 😅",
    " Will never answer a video call🏃‍♂",
    " Always carries candy 🍬",
    " They have so much wisdom to offer 😊",
    " Life is hard when I don't talk to them 😞",
    " Knows the precise time to post to get the most likes on instagram 😎",
    " Remember everyones birthday  🎂",
    " They have turned everyone into their simp 🤙",
    " Didn't realise how amazing they are 🤩",
    " Could travel the multiverse☄",
    " Could flirt their way into a discount 😜",
    " They are the bad influence every parent is worried about(not really)😆",
    " Could teach a university-level course on how to make perfect tea ☕",
    " Absolutely rocks their curly hair 👩‍🦱👨‍🦱",
    " I don't know them that well but I feel a connection with them 🫶",
    " They're just a baby 👶🏻",
    " They're never wrong🤫",
    " They are always chasing clout 🫢",
    " Want to spend your life with someone like them 💕",
    " Tries ten outfits on before choosing one 🫡",
    " Total life saver 🫵",
    " Most free-spirited person ever ☮",
    " Has the most complex handshakes 🤝",
    " Lets go watch a scary movie together 🍿",
    " They are irreplaceble 👥",
    " Never studies and still scores the highest 😐",
    " Teachers love them 😊",
    " Finishes test while everyone's still on second question 🤒",
    " Love football but never plays 😐",
    " You basically cannot hate them 💟",
    " Freshest presence 😁",
    " Talk to me I'm bored ‼",
    " They're probably born into royalty 👑",
    " I wish I could hug them forever 🫂",
    " Future doctor 🩺",
    " Dopest personality 😎",
    " Always has the latest mobile phone 📱",
    " I have a secret for you 😌",
    "'re one of a kind 😣",
    " a 'glass-half-full' Kinda person 😊",
    " I need something fixed(my heart) I call them 🛠",
    " likely to win a golgappe eating contest 😱",
    " buddy 🤫",
    " likely to have the highest snap-score? 😆",
    " besties with everyone 🥰",
    " the life of the party 🤩",
    " likely to be a hopeless romantic 😅",
    " only you would ask me to get coffee 🥰",
    " someone doesn't like you they're losing at life 😤",
    " test while everyones still on question 3 part a 🧐",
    " Cutest laugh that sounds like a steam-engine 😂",
    " Most chaotic school prankster 😬",
    " Could work in CID 🕵‍♀",
    " You can't forget their name no matter what 😻",
    " So photogenic 📸",
    " Who's my favorite person 😍",
    " They will never break someone's trust 💯",
    " Has the smallest circle with only the most real people 🥰",
    " I will fight anyone for you 🥊",
    " I have never seen them in class 😁",
    " They resemble a celebrity ⭐",
    " You're always comfortable around them 🫂",
    " Prefers wired headphones 🎧",
    " Celebrity of your gang",
    " drama but never participates 🙊",
    " They're the missing piece in my life 💖",
    "'re probably born into royalty 👑",
    " to me I'm bored!!!",
    " only name on my bff list 🫂",
    " basically cannot hate them 💟",
    " presence 😁",
    " constant crush since coming to the collage/school",
    " running a marathon through my dreams I need peace 🏃🏻‍♂",
    " with the tea-stall owner 🫱🏼‍🫲🏽",
    " The only person Iam comfortable sitting in silence with ☺",
    " I have shared the best laughs of my life with them 😇",
    " constant reassueance that their friends are not sick of them 🤣",
    " My parents don't know how naughty they actually are 🤕",
    " are desperately waiting for us to date 🧑🏻‍❤‍🧑🏻",
    "They make everything fun 😊",
    "Future fashion designer 👗",
    "Class story teller 🤩",
    "Always getting in troble 🤕",
    "BTS lover 💜",
    "Could give a tutorial on how to build a bomb 💣",
    "Secretly roasts every teacher 🥶",
    "PUBG addict 💥",
    " Always carry candy 🍬🍭",
    " You sure know how to sweep me off my feet 👣",
    " They have so much wisdom to offer 🤩",
    " Will never answer a video call ❌",
    " I do the craziest things to get them to notice me 😐",
    "The friend who always buys you food 🍔",
    "They don't pass the vibe check, they create it",
    "Keeps asking for food while traveling 🍕",
    "Says they're gonna rock the trip but sleeps for the entire trip 🤦‍♂",
    "Wears earphones though it does not work 😜",
    "Regret in current course 😪",
    "Looks fresh even without taking a bath 🚿",
    "Is always on Instagram 🙃",
    "Replys fast to you'r message's on whatsapp 😼",
    "Always stick's out their tongue while taking selfie 👅",
    "The friend who steals your cloth's 👕👚",
    " There's something wrong with my phone, could you try putting your number in it 🌝",
    "Can't handle pressure 😮‍💨",
    "I would get their name tattooed 〰",
    "Has multiple love languages 💕",
    "I will treat you better than your current bf/gf ❣",
    "They always see the best in people 😊",
    "CEO of making weird faces while taking selfies 😙",
    "Remind me to bring an oxygen cylinder the next time we meet 😶‍🌫",
    "Ghosts people all the time 👻",
    "The milk to my fruit loops 🍒",
    "Would download duolingo but never use it 😅",
    "Their pet hates me for no reason 😭",
    "Knows how to turn every obstacle into opportunity 💪",
    "Rocks their piercings 🤟🏽",
    "Never wants to grow up 👼",
    "The micro influencer of our town 🤳🏼",
    "Turns into hulk when their friend is in trouble 💪🏼",
    "They are super lucky for me 🍃",
    "Iam too shy around them 😳🫣",
    "They never sleep but somehow always have energy⚡",
    "I'd thank them first in my oscar acceptance speech 🏆",
    "They've impacted my life in ways they dont even know 😓",
    " Can't believe a word that comes out of their mouth 🤣",
    " Need constant reassurance that their friends are not sick of them 😅",
    " Will never answer a video call🏃‍♂",
    " Always carries candy 🍬",
    " They have so much wisdom to offer 😊",
    " Life is hard when I don't talk to them 😞",
    " Knows the precise time to post to get the most likes on instagram 😎",
    " Remember everyones birthday  🎂",
    " They have turned everyone into their simp 🤙",
    " Didn't realise how amazing they are 🤩",
    " Could travel the multiverse☄",
    " Could flirt their way into a discount 😜",
    " They are the bad influence every parent is worried about(not really)😆",
    " Could teach a university-level course on how to make perfect tea ☕",
    " Absolutely rocks their curly hair 👩‍🦱👨‍🦱",
    " I don't know them that well but I feel a connection with them 🫶",
    " They're just a baby 👶🏻",
    " They're never wrong🤫",
    " They are always chasing clout 🫢",
    " Want to spend your life with someone like them 💕",
    " Tries ten outfits on before choosing one 🫡",
    " Total life saver 🫵",
    " Most free-spirited person ever ☮",
    " Has the most complex handshakes 🤝",
    " Lets go watch a scary movie together 🍿",
    " They are irreplaceble 👥",
    " Never studies and still scores the highest 😐",
    " Teachers love them 😊",
    " Finishes test while everyone's still on second question 🤒",
    " Love football but never plays 😐",
    " You basically cannot hate them 💟",
    " Freshest presence 😁",
    " Talk to me I'm bored ‼",
    " They're probably born into royalty 👑",
    " I wish I could hug them forever 🫂",
    " Future doctor 🩺",
    " Dopest personality 😎",
    " Always has the latest mobile phone 📱",
    " I have a secret for you 😌",
    "'re one of a kind 😣",
    " a 'glass-half-full' Kinda person 😊",
    " I need something fixed(my heart) I call them 🛠",
    " likely to win a golgappe eating contest 😱",
    " buddy 🤫",
    " likely to have the highest snap-score? 😆",
    " besties with everyone 🥰",
    " the life of the party 🤩",
    " likely to be a hopeless romantic 😅",
    " only you would ask me to get coffee 🥰",
    " someone doesn't like you they're losing at life 😤",
    " test while everyones still on question 3 part a 🧐",
    " Cutest laugh that sounds like a steam-engine 😂",
    " Most chaotic school prankster 😬",
    " Could work in CID 🕵‍♀",
    " You can't forget their name no matter what 😻",
    " So photogenic 📸",
    " Who's my favorite person 😍",
    " They will never break someone's trust 💯",
    " Has the smallest circle with only the most real people 🥰",
    " I will fight anyone for you 🥊",
    " I have never seen them in class 😁",
    " They resemble a celebrity ⭐",
    " You're always comfortable around them 🫂",
    " Prefers wired headphones 🎧",
    " Celebrity of your gang",
    " drama but never participates 🙊",
    " They're the missing piece in my life 💖",
    "'re probably born into royalty 👑",
    " to me I'm bored!!!",
    " only name on my bff list 🫂",
    " basically cannot hate them 💟",
    " presence 😁",
    " constant crush since coming to the collage/school",
    " running a marathon through my dreams I need peace 🏃🏻‍♂",
    " with the tea-stall owner 🫱🏼‍🫲🏽",
    " The only person Iam comfortable sitting in silence with ☺",
    " I have shared the best laughs of my life with them 😇",
    " constant reassueance that their friends are not sick of them 🤣",
    " My parents don't know how naughty they actually are 🤕",
    " are desperately waiting for us to date 🧑🏻‍❤‍🧑🏻",
    "They make everything fun 😊",
    "Future fashion designer 👗",
    "Class story teller 🤩",
    "Always getting in troble 🤕",
    "BTS lover 💜",
    "Could give a tutorial on how to build a bomb 💣",
    "Secretly roasts every teacher 🥶",
    "PUBG addict 💥",
    " Always carry candy 🍬🍭",
    " You sure know how to sweep me off my feet 👣",
    " They have so much wisdom to offer 🤩",
    " Will never answer a video call ❌",
    " I do the craziest things to get them to notice me 😐",
    "The friend who always buys you food 🍔",
    "They don't pass the vibe check, they create it",
    "Keeps asking for food while traveling 🍕",
    "Says they're gonna rock the trip but sleeps for the entire trip 🤦‍♂",
    "Wears earphones though it does not work 😜",
    "Regret in current course 😪",
    "Looks fresh even without taking a bath 🚿",
    "Is always on Instagram 🙃",
    "Replys fast to you'r message's on whatsapp 😼",
    "Always stick's out their tongue while taking selfie 👅",
    "The friend who steals your cloth's 👕👚"
]

  for items in q:
    a = Question.objects.create(question = items)
    a.save()
  return Response("saved")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_member(request):
  req = request.data
  user = Profile.objects.get(email = req["email"])
  group = Group.objects.get(id = req["group"])
  members = Members.objects.get(user = user,group = group).delete()
  members = Members.objects.select_related("user","group").filter(group = group)
  serializer = MemberSerializer(members,many = True)
  return Response(serializer.data)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def delete_account(request):
  user = User.objects.get(username = request.user.username)
  prof = Profile.objects.get(email = request.user.username)
  groups = Group.objects.filter(admin = prof)
  if groups.exists():
    for items in groups:
      try:
        new_admin = Members.objects.filter(group = items).order_by("added")[1]
        items.admin = new_admin.user
        items.save()
      except IndexError:
        items.delete()
  user.delete()
  prof.delete()
  return Response("Deleted")


