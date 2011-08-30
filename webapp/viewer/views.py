from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert, ConfigForm
import persistent_messages
import time
from datetime import datetime, timedelta

def set_user(request):
    if not request.user.is_authenticated():
        user = authenticate(username='babby', password='onthemove')
        login(request, user)


def create_alert_obj():
    cur_time = round(time.time())
    type_switch = cur_time % 3
    alert_switch = cur_time % 5
    if alert_switch == 1:
        Alert.objects.create(event_type='motion' if type_switch else 'sound')

def get_alert_obj():
    alerts = Alert.objects.filter(timestamp__gte=datetime.now()-timedelta(seconds=10)).order_by('timestamp')
    if len(alerts):
        return alerts[0]

def set_up_alert(request):
    create_alert_obj()
    alert = get_alert_obj()
    if alert:
        if alert.event_type == 'motion':
            persistent_messages.add_message(request, persistent_messages.WARNING, 'The babby is on the move!', extra_tags='warning', email=True)
        else:
            persistent_messages.add_message(request, persistent_messages.WARNING, 'The babby is crying!', extra_tags='warning', email=True)

def toggle_sms(request):
    if request.method == 'POST' and request.POST.get('toggle_sms', None):
        profile = request.user.get_profile()

        profile.sms_on = False if profile.sms_on else True
        profile.save()

        on_off = 'ON' if profile.sms_on else 'OFF'

        messages.info(request, 'SMS Notifications have been turned {0}'.format(on_off), extra_tags='success')


def index(request):
    set_user(request)
    set_up_alert(request)
    toggle_sms(request)

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


