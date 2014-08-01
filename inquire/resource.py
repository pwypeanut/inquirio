# Requests for Resources
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpRequest
from django.template.response import TemplateResponse

import os

RESOURCE_PATH = "/home/action/inquirio/inquire/resources/"

ALLOWED_RESOURCES = [
  'js/jquery.min.js',
  'js/jquery.cookie.js',
  'js/jquery.qtip.min.js',
  'js/masonry.min.js',
  'js/stellar.min.js',
  'css/login.css',
  'css/normalize.css',
  'css/home.css',
  'css/quiz.css',
  'img/squared_metal.png',
  'img/inquirio.png',
  'img/classroom.png',
]

MAPPED_EXTENSIONS = [
  ['.js', 'text/javascript'],
  ['.css', 'text/css'],
  ['.png', 'image/png'],
]

urlpatterns = [
  url(r'', 'inquire.resource.get_resource'),
]

def get_resource(request):
  for res in ALLOWED_RESOURCES:
    if os.path.join("/resources/", res) == request.path:
      filepath = open(os.path.join(RESOURCE_PATH, res), 'r')
      response = HttpResponse(content = filepath.read())
      for ext in MAPPED_EXTENSIONS:
        filename, fileext = os.path.splitext(res)
        if fileext == ext[0]:
          response['Content-Type'] = ext[1]
      return response
  return HttpResponseNotFound("")