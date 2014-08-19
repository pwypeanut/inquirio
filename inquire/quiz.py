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
from models import Subtopic, Topic, Question, QuestionOption, Quiz, QuizResponse
from json import JSONEncoder
import json, time
from django.core.mail import send_mail
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = [
  url(r'^create/$', 'inquire.quiz.create'),
  url(r'^summary/(?P<quiz_id>\w+)/$', 'inquire.quiz.summary'),
  url(r'^close/(?P<quiz_id>\w+)/$', 'inquire.quiz.close'),
  url(r'^attempt/(?P<quiz_id>\w+)/$', 'inquire.quiz.attempt'),
  url(r'^get/(?P<quiz_id>\w+)/(?P<qn_number>[0-9]+)/$', 'inquire.quiz.get'),
  url(r'^try/(?P<quiz_id>\w+)/(?P<qn_number>[0-9]+)/$', 'inquire.quiz.try_question'),
]

from inquire.get import question_to_array

@login_required
def get(request, quiz_id, qn_number):
   try:
       quiz = Quiz.objects.get(url = quiz_id)
   except:
       return HttpResponseNotFound()
   questions = quiz.questions.all()
   return HttpResponse(question_to_array(questions[int(qn_number) - 1]))

@login_required
def try_question(request, quiz_id, qn_number):
   answer_text = request.POST.get("option")
   try:
       quiz = Quiz.objects.get(url = quiz_id)
   except:
       return HttpResponseNotFound()
   questions = quiz.questions.all()
   try:
       answer = QuestionOption.objects.get(question = questions[int(qn_number) - 1], text = answer_text)
   except QuestionOption.DoesNotExist:
       return HttpResponseNotFound()
   response = QuizResponse(quiz = quiz, question = questions[int(qn_number) - 1], chosen_answer = answer, user = request.user)
   try:
       QuizResponse.objects.get(quiz = quiz, question = questions[int(qn_number) - 1], user = request.user)
   except:
       response.save()
       return HttpResponse()
   else:
       return HttpResponseNotFound()

@login_required
def attempt(request, quiz_id):
   try:
       quiz = Quiz.objects.get(url = quiz_id)
   except:
       return HttpResponseNotFound()
   return render_to_response("custom_quiz.html", {
     'quiz_id': quiz_id,
     'quiz_length': quiz.questions.all().count(),
   })

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

def request_summary(request, quiz_id):
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
  emailmsg = emailmsg.replace("%timestamp%", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  
  answers_str = ""
  
  qn_count = 0
  for qn in quiz.questions.all():
    qn_count += 1
    options = QuestionOption.objects.filter(question = qn)
    correct_option = QuestionOption.objects.get(question = qn, correct_answer = True)
    
    correct_answers = QuizResponse.objects.filter(quiz = quiz, question = qn, chosen_answer = correct_option).count()
    wrong_answers = QuizResponse.objects.filter(quiz = quiz, question = qn).count() - correct_answers
    answers_str += "\t" + str(qn_count) + ". " + qn.text + " (" + str(correct_answers) + " correct, " + str(wrong_answers) + " wrong)\n"
    for op in options:
      responses = QuizResponse.objects.filter(quiz = quiz, question = qn, chosen_answer = op)
      answers_str += "\t" + "Option: " + op.text + " (" + str(responses.count()) + ") --> "
      if responses.count() == 0:
        answers_str += "None"
      else:
        for res in responses:
          answers_str += res.user.username + ". "
      answers_str += "\n"
    answers_str += "\n"
  
  emailmsg = emailmsg.replace("%answers%", answers_str)
  send_mail("Summary of Responses: " + quiz_id, emailmsg, "verify@inquirio.sg", [request.user.email], fail_silently = False)

@login_required
def summary(request, quiz_id):
  try:
    quiz = Quiz.objects.get(url = quiz_id)
  except:
    return HttpResponseNotFound()
  
  if quiz.author != request.user:
    return HttpResponseNotFound()
  request_summary(request, quiz_id)
  return HttpResponse("An email has been sent.")

@login_required
def close(request, quiz_id):
  try:
    quiz = Quiz.objects.get(url = quiz_id)
  except:
    return HttpResponseNotFound()
  
  if quiz.author != request.user:
    return HttpResponseNotFound()
    
  request_summary(request, quiz_id)
  
  quiz.delete()
  
  return HttpResponse("The quiz has been closed.")