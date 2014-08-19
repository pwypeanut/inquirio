from django.contrib import admin
import models

# Register your models here.
admin.site.register(models.Question)
admin.site.register(models.QuestionOption)
admin.site.register(models.Topic)
admin.site.register(models.Subtopic)
admin.site.register(models.Answered)
admin.site.register(models.Quiz)
admin.site.register(models.QuizResponse)