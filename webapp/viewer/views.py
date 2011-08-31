from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from viewer.models import Alert, ConfigForm, User
import persistent_messages
#import time
from datetime import datetime, timedelta

def set_user(request):
    if not request.user.is_authenticated():
        user = authenticate(username='babby', password='onthemove')
        login(request, user)

        request.session['sender_user'] = User.objects.filter(pk=2) # get the partytime user for sending emails to

def get_new_recent_alerts(request):
    user = authenticate(username='babby', password='onthemove')

    alerts = Alert.objects.filter(timestamp__gte=datetime.now()-timedelta(seconds=5)).order_by('timestamp')
    if len(alerts):
        persistent_messages.add_message(
                request,
                persistent_messages.WARNING,
                message='The babby is on the move!',
                subject='Alert',
                extra_tags='warning',
                email=False,
                #user=user,
                #from_user=request.session['sender_user'],
                fail_silently=True
        )


def alerts_ajax(request):
    get_new_recent_alerts(request)

    return render_to_response('messages.html', {}, context_instance=RequestContext(request))

def toggle_sms(request):
    if request.method == 'POST' and request.POST.get('toggle_sms', None):
        profile = request.user.get_profile()

        profile.sms_on = False if profile.sms_on else True
        profile.save()

        on_off = 'ON' if profile.sms_on else 'OFF'

        messages.info(request, 'SMS Notifications have been turned {0}'.format(on_off), extra_tags='success')


def index(request):
    set_user(request)
    get_new_recent_alerts(request)
    toggle_sms(request)

    sms_status = 'ON' if request.user.get_profile().sms_on else 'OFF'

    return render_to_response('index.html',
            {'sms_status': sms_status},
            context_instance=RequestContext(request))

def log(request):
    set_user(request)
    get_new_recent_alerts(request)

    return render_to_response('log.html',
                              {},
                              context_instance=RequestContext(request))

def configure(request):
    set_user(request)
    get_new_recent_alerts(request)

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


