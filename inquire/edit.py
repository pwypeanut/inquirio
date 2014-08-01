from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from models import Question, QuestionOption
from django.conf.urls import url
import json

urlpatterns = [
  url(r'^question/(?P<question_id>[0-9]+)/$', 'inquire.edit.question'),
  url(r'^options/(?P<question_id>[0-9]+)/$', 'inquire.edit.options'),
]

@login_required
def question(request, question_id):
  new_question = request.POST.get("new_question")
  try:
    question = Question.objects.get(id = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseForbidden()
  question.text = new_question
  question.save()
  return HttpResponse()

@login_required
def options(request, question_id):
  new_options = json.loads(request.POST.get("new_options"))
  try:
    question = Question.objects.get(id = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseForbidden()
  try:
    correct_answer = QuestionOption.objects.get(question = question, correct_answer = True)
  except QuestionOption.DoesNotExist:
    pass
  except QuestionOption.MultipleObjectsReturned:
    correct_answer = QuestionOption.objects.filter(question = question, correct_answer = True)[0]
  QuestionOption.objects.filter(question = question).delete()
  for new_option in new_options:
    if new_option == correct_answer.text:
      option = QuestionOption.create(question = question, text = new_option, correct_answer = True)
      option.save()
    else:
      option = QuestionOption.create(question = question, text = new_option, correct_answer = False)
      option.save()
  return HttpResponse()