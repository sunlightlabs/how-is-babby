from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert, ConfigForm
import persistent_messages
import time

def set_user(request):
    if not request.user.is_authenticated():
        user = authenticate(username='babby', password='onthemove')
        login(request, user)


def set_up_alert(request):
    for alert in Alert.objects.all():
        if alert.event_type == 'motion':
            persistent_messages.add_message(request, persistent_messages.WARNING, 'The babby is on the move!', extra_tags='warning', email=True)
        else:
            persistent_messages.add_message(request, persistent_messages.WARNING, 'The babby is crying!', extra_tags='warning', email=True)
        alert.delete()


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


