from django.conf.urls.defaults import *

urlpatterns = patterns('',

                       url(r'^$',
                        'viewer.views.index',
                        {},
                        name='viewer_index')
)
