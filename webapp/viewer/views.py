from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert
import time

def get_alert_obj():
    cur_time = round(time.time())
    type_switch = cur_time % 3
    alert_switch = cur_time % 5
    if alert_switch == 1:
        return Alert.objects.create(event_type='motion' if type_switch else 'sound')
    else:
        return None

def set_up_alert(request):
    alert = get_alert_obj()
    if alert:
        if alert.event_type == 'motion':
            messages.info(request, 'The babby is on the move!')
        else:
            messages.info(request, 'The babby is crying!')

def index(request):
    set_up_alert(request)

    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def log(request):
    set_up_alert(request)

    return render_to_response('log.html',
                              {},
                              context_instance=RequestContext(request))

def configure(request):
    set_up_alert(request)

    return render_to_response('configure.html',
                              {},
                              context_instance=RequestContext(request))

