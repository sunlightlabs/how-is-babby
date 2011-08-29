from django.conf.urls.defaults import *

urlpatterns = patterns('',

   url(r'^/log$', 'viewer.views.log', {}, name='viewer_eventlog'),
   url(r'^$', 'viewer.views.index', {}, name='viewer_index'),
)
