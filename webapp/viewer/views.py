from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert, ConfigForm
from django.forms.models import model_to_dict
import time

def set_user(request):
    if not request.user.is_authenticated():
        user = authenticate(username='babby', password='onthemove')
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
            messages.info(request, 'The babby is on the move!', extra_tags='warning')
        else:
            messages.info(request, 'The babby is crying!', extra_tags='warning')

def index(request):
    set_user(request)
    set_up_alert(request)

    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def log(request):
    set_user(request)
    set_up_alert(request)

    return render_to_response('log.html',
                              {},
                              context_instance=RequestContext(request))

def configure(request):
    set_user(request)
    set_up_alert(request)

    profile = request.user.get_profile()

    if request.method == 'POST':
        form = ConfigForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.info(request, 'Settings saved!', extra_tags='success')
        else:
            messages.error(request, 'There was a problem saving your form.', extra_tags='error')
    else:
        form = ConfigForm(instance=request.user.get_profile())

    return render_to_response('configure.html',
                              {'form': form },
                              context_instance=RequestContext(request))

