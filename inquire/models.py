from django.db import models
from django.contrib.auth.models import User
import utils, math

class QuestionOption(models.Model):
  text = models.CharField(max_length = 128)
  question = models.ForeignKey("Question")
  correct_answer = models.BooleanField()
  def __unicode__(self):
    return self.question.subtopic.topic.name + " / " + self.question.subtopic.name + ": " + self.question.text + " (" + self.text + ")"

class Question(models.Model):
  text = models.CharField(max_length = 512)
  subtopic = models.ForeignKey("Subtopic")
  author = models.ForeignKey(User)
  date_created = models.DateField(auto_now = True)
  correct_tries = models.IntegerField()
  wrong_tries = models.IntegerField()
  @property
  def difficulty(self): # Out of 1
    if correct_tries + wrong_tries == 0:
      return 0.1711
    else:
      return ((correct_tries + 1.9208) / (correct_tries + wrong_tries) - 1.96 * math.sqrt((correct_tries * wrong_tries) / (correct_tries + wrong_tries) + 0.9604) / (correct_tries + wrong_tries)) / (1 + 3.8416 / (correct_tries + wrong_tries))
  def __unicode__(self):
    return self.subtopic.topic.name + " / " + self.subtopic.name + ": " + self.text
  
class Topic(models.Model):
  name = models.CharField(max_length = 32)
  def __unicode__(self):
    return self.name
  @property
  def tag_name(self):
    return self.name.lower().replace(" ", "-")
  
class Subtopic(models.Model):
  name = models.CharField(max_length = 32)
  topic = models.ForeignKey("Topic")
  def __unicode__(self):
    return self.topic.name + ": " + self.name
  @property
  def tag_name(self):
    return self.topic.tag_name
  @property
  def question_count(self):
    return Question.objects.filter(subtopic = self).count()
  def unanswered_count(self, user):
    return Question.objects.filter(subtopic = self).count() - Answered.objects.filter(question__subtopic = self, user = user).count()
  
class Answered(models.Model):
  user = models.ForeignKey(User)
  question = models.ForeignKey("Question")
  def __unicode__(self):
    return self.user.username + " answered " + self.question.text