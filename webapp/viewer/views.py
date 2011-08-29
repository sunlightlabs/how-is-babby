from django.shortcuts import render_to_response
<<<<<<< HEAD
# Create your views here.

def index(request):
    return render_to_response('index.html', request)

=======
from django.template import RequestContext

def index(request):
    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))
>>>>>>> 5435ed9096e60ef576d7e1f67c86669c3eece97f
