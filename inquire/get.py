# Requests for Questions
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpRequest
from django.template.response import TemplateResponse
from models import Subtopic, Answered, QuestionOption, Question
from json import JSONEncoder
import random

urlpatterns = [
  url(r'(?P<subtopic>[0-9]+)', 'inquire.get.get_question'),
]

def date_convert(dt):
  return str(dt.year) + "/" + str(dt.month) + "/" + str(dt.day)

def question_to_array(qn):
  qn_info = []
  qn_info.append(qn.id)
  qn_info.append(qn.subtopic.name)
  qn_info.append(qn.text)
  try:
    qn_options = QuestionOption.objects.filter(question = qn)
  except QuestionOption.DoesNotExist:
    qn_options = []
  qn_optiontext = []
  for option in qn_options:
    qn_optiontext.append(option.text)
  qn_info.append(qn_optiontext)
  qn_info.append(qn.author.username)
  qn_info.append(date_convert(qn.date_created))
  return JSONEncoder().encode(qn_info)

def get_question(request, subtopic):
  try:
    subtopic = Subtopic.objects.get(id = subtopic)
  except Subtopic.DoesNotExist:
    return HttpResponse("[]")
  if subtopic.unanswered_count(request.user) == 0:
    return HttpResponse("[]")
  else:
    try:
      questions = Question.objects.filter(subtopic = subtopic)
    except Question.DoesNotExist:
      return HttpResponse("[]")
    questions1 = []
    for qn in questions:
      questions1.append(qn)
    random.shuffle(questions1)
    for qn in questions1:
      try:
        Answered.objects.get(user = request.user, question = qn)
      except Answered.DoesNotExist:
        return HttpResponse(question_to_array(qn))
  return HttpResponse("[]")