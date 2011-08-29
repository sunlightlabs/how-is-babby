from django.conf.urls.defaults import *

urlpatterns = patterns('',

   url(r'log$', 'viewer.views.log', {}, name='viewer_log'),
   url(r'configure$', 'viewer.views.configure', {}, name='viewer_configure'),
   url(r'^$', 'viewer.views.index', {}, name='viewer_index'),
)
