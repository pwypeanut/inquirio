from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpRequest
from django.template.response import TemplateResponse
from models import Subtopic, Answered, QuestionOption, Question
from json import JSONEncoder

urlpatterns = [
  url(r'(?P<question>[0-9]+)', 'inquire.attempt.try_question'),
]

def try_question(request, question):
  try:
    qn_check = Answered.objects.get(question = question, user = request.user)
  except Answered.DoesNotExist:
    pass
  else:
    return HttpResponseNotFound()
  try:
    qn = Question.objects.get(id = question)
  except Question.DoesNotExist:
    return HttpResponseNotFound()
  ans = request.POST.get("option")
  try:
    qn_option = QuestionOption.objects.get(question = qn, text = ans)
  except QuestionOption.DoesNotExist:
    return HttpResponseNotFound()
  if qn_option.correct_answer == True:
    entry = Answered(user = request.user, question = qn)
    qn.correct_tries += 1
    qn.save()
    entry.save()
    return HttpResponse("1")
  else:
    qn.wrong_tries += 1
    qn.save()
    return HttpResponse("0")