from django.shortcuts import render
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from models import Subtopic, Topic
from json import JSONEncoder


urlpatterns = [
  url(r'^$', 'inquire.views.root_page'),
  url(r'^home/$', 'inquire.views.home'),
  url(r'^manage/$', 'inquire.views.manage'),
  url(r'^login/$', 'inquire.views.login'),
  url(r'^logout/$', 'inquire.views.logout_then_login'),
  url(r'^practice/(?P<topics>[0-9-]+)/$', 'inquire.views.practice'),
  url(r'^quiz/(?P<topics>[0-9-]+)/(?P<question>[0-9]+)/$', 'inquire.views.quiz'),
]

# Create your views here.
def root_page(request):
  if request.user.is_authenticated() == False:
    return HttpResponseRedirect("/login/")
  else:
    return HttpResponseRedirect("/home/")
  
def login(request):
  if request.user.is_authenticated() == False:
    c = {}
    c.update(csrf(request))
    return render_to_response("login.html", c)
  else:
    return HttpResponseRedirect("/home/")

@login_required
def home(request):
  subtopics = Subtopic.objects.all()
  for subtopic in subtopics:
    subtopic.unanswered = subtopic.unanswered_count(request.user)
  if request.user.is_superuser:
    title = "Administrator"
  else:
    title = "Suanner"
  return render_to_response("home.html", {
      'subtopics': subtopics,
      'topics': Topic.objects.all(),
      'user': request.user,
      'title': title,
  })

@login_required
def manage(request):
  if request.user.is_superuser:
    title = "Administrator"
  else:
    title = "Suanner"
  return render_to_response("manage.html", {
      'subtopics': Subtopic.objects.all(),
      'topics': Topic.objects.all(),
      'user': request.user,
      'title': title,
  })

@login_required
def practice(request, topics):
  topics = topics.split("-")
  for i in range(len(topics)):
    try:
      topics[i] = int(topics[i])
    except ValueError:
      return HttpResponseNotFound()
  
  return render_to_response("quiz.html", {
    'subtopics': JSONEncoder().encode(topics)  
  })

@login_required
def quiz(request, topics, question):
  return HttpResponse("quizzing")