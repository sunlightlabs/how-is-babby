from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert, ConfigForm
import time

def login(request):
    user = authenticate(username='babby', password='onthemove')
    if not request.user:
        login(request, user)


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
    login(request)
    set_up_alert(request)

    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def log(request):
    login(request)
    set_up_alert(request)

    return render_to_response('log.html',
                              {},
                              context_instance=RequestContext(request))

def configure(request):
    login(request)
    set_up_alert(request)

    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            config = request.user.get_profile()
            d = form.cleaned_data

            # set all the fields
            config['motion_sensitivity'] = d['motion_sensitivity']
            config['sound_sensitivity'] = d['sound_sensitivity']
            config['distance'] = d['distance']
            config['sms_email'] = d['sms_email']
            config['sms_on'] = d['sms_on']
            config['nightvision_on'] = d['nightvision_on']

            config.save()
    else:
        form = ConfigForm()

    return render_to_response('configure.html',
                              {'form': form },
                              context_instance=RequestContext(request))

