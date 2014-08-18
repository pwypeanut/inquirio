from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from models import Question, QuestionOption, Subtopic
from django.conf.urls import url
import json

urlpatterns = [
  url(r'^question/(?P<question_id>\w+)/$', 'inquire.edit.question'),
  url(r'^options/(?P<question_id>\w+)/$', 'inquire.edit.options'),
  url(r'^answer/(?P<question_id>\w+)/$', 'inquire.edit.answer'),
  url(r'^delete/(?P<question_id>\w+)/$', 'inquire.edit.delete'),
  url(r'^public/(?P<question_id>\w+)/$', 'inquire.edit.public'),
  url(r'^private/(?P<question_id>\w+)/$', 'inquire.edit.private'),
  url(r'^verify/$', 'inquire.edit.verify'),
  url(r'^add/$', 'inquire.edit.add'),
]

@login_required
def question(request, question_id):
  new_question = request.POST.get("new_question")
  try:
    question = Question.objects.get(unique_identifier = question_id)
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
    question = Question.objects.get(unique_identifier = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseNotFound()
  correct_answer = None
  try:
    correct_answer = QuestionOption.objects.get(question = question, correct_answer = True)
  except QuestionOption.DoesNotExist:
    pass
  except QuestionOption.MultipleObjectsReturned:
    correct_answer = QuestionOption.objects.filter(question = question, correct_answer = True)[0]
  QuestionOption.objects.filter(question = question).delete()
  for new_option in new_options:
    if correct_answer == None:
      option = QuestionOption(question = question, text = new_option, correct_answer = False)
      option.save()
    elif new_option == correct_answer.text:
      option = QuestionOption(question = question, text = new_option, correct_answer = True)
      option.save()
    else:
      option = QuestionOption(question = question, text = new_option, correct_answer = False)
      option.save()
  return HttpResponse()

@login_required
def answer(request, question_id):
  new_answer = request.POST.get("new_answer")
  try:
    question = Question.objects.get(unique_identifier = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseNotFound()
  try:
    correct_option = QuestionOption.objects.get(question = question, text = new_answer)
  except QuestionOption.DoesNotExist:
    return HttpResponse()
  old_answers = QuestionOption.objects.filter(question = question, correct_answer = True)
  for old_answer in old_answers:
    old_answer.correct_answer = False
    old_answer.save()
  correct_option.correct_answer = True
  correct_option.save()
  return HttpResponse()

@login_required
def delete(request, question_id):
  try:
    question = Question.objects.get(unique_identifier = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseForbidden()
  QuestionOption.objects.filter(question = question).delete()
  question.delete()
  return HttpResponse()

@login_required
def public(request, question_id):
  try:
    question = Question.objects.get(unique_identifier = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseForbidden()
  question.visible = True
  question.save()
  return HttpResponse()

@login_required
def private(request, question_id):
  try:
    question = Question.objects.get(unique_identifier = question_id)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  if request.user != question.author:
    return HttpResponseForbidden()
  question.visible = False
  question.save()
  return HttpResponse()

@login_required
def verify(request):
  current_id = request.POST.get("current_id")
  current_qn = request.POST.get("current_qn")
  try:
    question = Question.objects.get(id = current_id)
    if question.text == current_qn:
      return HttpResponse()
    else:
      return HttpResponse("error")
  except Question.DoesNotExist:
    return HttpResponse("error")
  
@login_required
def add(request):
  subtopic_id = request.POST.get("section")
  question_text = request.POST.get("question_text")
  try:
    subtopic = Subtopic.objects.get(id = subtopic_id)
  except Subtopic.DoesNotExist:
    return HttpResponseNotFound()
  new_question = Question(text = question_text, author = request.user, subtopic = subtopic, correct_tries = 0, wrong_tries = 0, visible = False)
  new_question.save()
  return HttpResponse(new_question.unique_identifier)