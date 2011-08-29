from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def log(request):
    return render_to_response('log.html',
                              {},
                              context_instance=RequestContext(request))

def configure(request):
    return render_to_response('configure.html',
                              {},
                              context_instance=RequestContext(request))

