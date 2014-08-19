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
from models import Subtopic, Topic, Question, QuestionOption, Quiz
from json import JSONEncoder
import json, time
from django.core.mail import send_mail
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = [
  url(r'^create/$', 'inquire.quiz.create'),
  url(r'^summary/(?P<quiz_id>\w+)/$', 'inquire.quiz.summary'),
  url(r'^close/(?P<quiz_id>\w+)/$', 'inquire.quiz.close'),
]

@login_required
def create(request):
  if request.method == "GET":
    questions = Question.objects.filter(author = request.user)
    for qn in questions:
      try:
        question_answer = QuestionOption.objects.get(question = qn, correct_answer = True)
      except:
        qn.answer = "None"
      else:
        qn.answer = question_answer.text
      qn.subtopic_name = qn.subtopic.name

    if request.user.is_superuser:
      title = "Administrator"
    else:
      title = "Suanner"

    return render_to_response("quiz_create.html", {
        'questions': questions,
        'user': request.user,
        'title': title,
    })
  else:
    questions = json.loads(request.POST.get("questions"))
    questions_list = []
    for qid in questions:
      questions_list.append(Question.objects.get(unique_identifier = qid))
    new_quiz = Quiz(author = request.user)
    new_quiz.save()
    for qn in questions_list:
      new_quiz.questions.add(qn)
    new_quiz.save()
    emailmsg = """
    Dear %username%,
    
    Your new quiz %identifier% has been created!
    
    The questions included in this quiz are:
%questions%
    
    Participants of the quiz should visit http://inquirio.sg/quiz/attempt/%identifier%/ .
    
    A summary of the quiz can be requested through http://inquirio.sg/quiz/summary/%identifier%/ . The quiz summary will be sent to you via email.
    
    To close the quiz, please visit http://inquirio.sg/quiz/close/%identifier%/ . A final summary email will be sent to you before the quiz is closed.
    
    Thank you!
    
    Regards,
    The Administrators of Inquirio.
    """
    
    emailmsg = emailmsg.replace("%username%", request.user.username)
    emailmsg = emailmsg.replace("%identifier%", new_quiz.url)
    questions_str = ""
    for qn in questions_list:
      questions_str += "\t" + qn.__unicode__() + "\n"
    emailmsg = emailmsg.replace("%questions%", questions_str)
    print emailmsg
    send_mail("New Quiz Created: " + new_quiz.url, emailmsg, "verify@inquirio.sg", [request.user.email], fail_silently = False)
    return HttpResponse()
  
@login_required
def summary(request, quiz_id):
  try:
    quiz = Quiz.objects.get(url = quiz_id)
  except:
    return HttpResponseNotFound()
  
  if quiz.author != request.user:
    return HttpResponseNotFound()
  
  emailmsg = """
  Dear %username%,
  
  Summary of quiz %identifier% as of %timestamp% has been requested.

%answers%
  
  Thank you!
  
  Regards,
  The Administrators of Inquirio.
  """
  
  emailmsg = emailmsg.replace("%username%", request.user.username)
  emailmsg = emailmsg.replace("%identifier%", quiz_id)
  emailmsg = emailmsg.replace("%timestamp%", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)))
  
  answers_str = ""
  
  qn_count = 0
  for qn in quiz.questions:
    qn_count += 1
    answers_str += "\t" + str(qn_count) + ". " + qn.text + "\n"
    options = QuestionOption.objects.get(question = qn)
    for op in options:
      responses = QuizResponse.objects.get(quiz = quiz, question = qn, chosen_answer = options)
      answers_str += "\t" + "Option: " + op.text + " (" + responses.count() + ")" + "\n"
    answers_str += "\n"
  
  emailmsg = emailmsg.replace("%answers%", answers_str)
  send_mail("Summary of Responses: " + quiz_id, emailmsg, "verify@inquirio.sg", [request.user.email], fail_silently = False)
  return HttpResponse()

@login_required
def close(request, quiz_id):
  return HttpResponse()