# Requests for Forms
from django.shortcuts import render
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
import hashlib
import os

urlpatterns = [
  url(r'^login/$', 'inquire.form.login_page'),
  url(r'^register/$', 'inquire.form.register'),
  url(r'^verify/', 'inquire.form.verify')
]

def generate_verification_key(user_id, username, user_email):
  hashans = hashlib.md5()
  hashans.update(str(user_id).encode('utf-8'))
  hashans.update(str(username).encode('utf-8'))
  hashans.update(str(user_email).encode('utf-8'))
  return hashans.hexdigest()

def login_page(request):
  requser = request.POST.get('username')
  reqpass = request.POST.get('password')
  matcheduser = authenticate(username = requser, password = reqpass)
  
  # Check if authentication is successful.
  if matcheduser is not None:
    if matcheduser.is_active:
      login(request, matcheduser)
      return HttpResponse("[1, \"Login correct.\"]")
    else:
      return HttpResponse("[0, \"User is not verified.\"]")
  else:
    return HttpResponse("[0, \"Login Incorrect.\"]")

def register(request):
  requser = request.POST.get('username')
  reqemail = request.POST.get('email')
  reqpass = request.POST.get('password')
  reqpass_repeat = request.POST.get('repeat_password')
  
  # Check if username field is empty.
  if requser == "" or requser == None:
    return HttpResponse("[0, \"Username cannot be empty.\"]")
  
  # Check if email field is empty.
  if reqemail == "" or reqemail == None:
    return HttpResponse("[0, \"Email cannot be empty.\"]")
  
  # Check if password field is empty.
  if reqpass == "" or reqpass == None:
    return HttpResponse("[0, \"Password cannot be empty.\"]")
  
  # Check if repeat password is empty.
  if reqpass_repeat == "" or reqpass_repeat == None:
    return HttpResponse("[0, \"Please repeat your password.\"]")
  
  # Check if two password fields are the same.
  if reqpass != reqpass_repeat:
    return HttpResponse("[0, \"Passwords do not match.\"]")
  
  # Check if username length within range.
  if len(requser) < 6:
    return HttpResponse("[0, \"Username must be at least 6 characters.\"]")
  if len(requser) > 20:
    return HttpResponse("[0, \"Username must be at most 20 characters.\"]")
  
  # Check if email length is within range.
  if len(reqemail) > 50:
    return HttpResponse("[0, \"Email must be at most 50 characters.\"]")
  
  # Check if password length is within range.
  if len(reqpass) < 6:
    return HttpResponse("[0, \"Password must be at least 6 characters.\"]")
  if len(reqpass) > 30:
    return HttpResponse("[0, \"Password must be at most 30 characters.\"]")
  
  # Check if username is valid
  if not requser.isalnum():
    return HttpResponse("[0, \"Username is invalid.\"]")
  
  # Check if email is valid
  try:
    validate_email(reqemail)
  except ValidationError as e:
    return HttpResponse("[0, \"Email is invalid.\"]")
  
  # Check for duplicate usernames
  try:
    duplicate_users = User.objects.get(username = requser)
  except User.DoesNotExist as e:
    pass
  else:
    return HttpResponse("[0, \"Username unavailable.\"]")
  
  # Check for duplicate emails
  try:
    duplicate_emails = User.objects.get(email = reqemail)
  except User.DoesNotExist as e:
    pass
  else:
    return HttpResponse("[0, \"Email has been used.\"]")
  
  # All checks passed. Create new user.
  newuser = User.objects.create_user(requser, reqemail, reqpass)
  newuser.is_active = False
  newuser.save()
  
  # Generate verification email.
  emailmsg = """
Dear %username%,

Welcome to Inquirio! Please confirm your user credentials:
Username: %username%
Email: %email%

In addition, please go to %domain%/forms/verify/%hashkey%/ to verify your account. If you did not sign up for Inquirio, please ignore this email.

Regards,
The Administrators of Inquirio.

NOTE: This is a computer-generated email. Please do not reply to this address.
  """
  
  emailmsg = emailmsg.replace("%username%", requser)
  emailmsg = emailmsg.replace("%email%", reqemail)
  emailmsg = emailmsg.replace("%domain%", "http://inquirio.sg")
  emailmsg = emailmsg.replace("%hashkey%", generate_verification_key(newuser.id, requser, reqemail))

  # Send verification email.
  send_mail("Inquirio Account Verification",
            emailmsg.encode('utf-8'),
            "verify@inquirio.sg",
            [reqemail]
  )
  
  return HttpResponse("[1, \"User created! Please verify your email.\"]")

def verify(request):
  verification_key = os.path.basename(os.path.normpath(request.path))
  all_users = User.objects.all()
  for user in all_users:
    if not user.is_active:
      correct_key = generate_verification_key(user.id, user.username, user.email)
      if correct_key == verification_key:
        user.is_active = True
        user.save()
        return HttpResponseRedirect("/login/")
  return HttpResponse("Verification Key not found.")
