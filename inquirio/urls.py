from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'inquirio.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^forms/', include('inquire.form')),
    url(r'^get/', include('inquire.get')),
    url(r'^attempt/', include('inquire.attempt')),
    url(r'^query/', include('inquire.query')),
    url(r'^edit/', include('inquire.edit')),
    url(r'^', include('inquire.views')),
)
