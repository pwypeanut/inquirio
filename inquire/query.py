from django.shortcuts import render
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from json import JSONEncoder
from models import Subtopic, Topic, Question, QuestionOption

urlpatterns = [
  url(r'^subtopic/(?P<topic_id>[0-9]+)', 'inquire.query.subtopic'),
  url(r'^auth_questions/(?P<subtopic_id>[0-9]+)', 'inquire.query.auth_questions'),
]

def subtopic(request, topic_id):
  try:
    topic = Topic.objects.get(id = topic_id)
  except Topic.DoesNotExist:
    return HttpResponseNotFound()
  subtopics = Subtopic.objects.filter(topic = topic)
  subtopic_name = []
  for st in subtopics:
    subtopic_name.append({
        'name': st.name,
        'id': st.id,
    })
  return HttpResponse(JSONEncoder().encode(subtopic_name))


def question_to_array(qn):
  qn_info = []
  qn_info.append(qn.id)
  qn_info.append(qn.text)
  qn_options = QuestionOption.objects.filter(question = qn)
  qn_optiontext = []
  qn_correctans = "undefined"
  for option in qn_options:
    qn_optiontext.append(option.text)
    if option.correct_answer:
      qn_correctans = option
  qn_info.append(qn_optiontext)
  if qn_correctans != "undefined":
    qn_info.append(qn_correctans.text)
  else:
    qn_info.append("-")
  qn_info.append(qn.correct_tries)
  qn_info.append(qn.wrong_tries)
  return qn_info

def auth_questions(request, subtopic_id):
  try:
    subtopic = Subtopic.objects.get(id = subtopic_id)
  except Subtopic.DoesNotExist:
    return HttpResponseNotFound()
  questions = Question.objects.filter(subtopic = subtopic, author = request.user)
  question_array = []
  for qn in questions:
    question_array.append(question_to_array(qn))
  return HttpResponse(JSONEncoder().encode(question_array))
  