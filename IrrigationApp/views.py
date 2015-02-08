from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time

from IrrigationApp.models import UserProfile, SimpleSchedule, RepeatableSchedule, WeatherHistory, Segment, Switch, Sensor

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests

def showMenu(request):
    return render(request, 'IrrigationApp/pages/menu.html')

def doLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        #User authentication successful
        login(request, user)
        try:
            return redirect('/getSystemStatus')
        except:
            return HttpResponse('Error during login: ' + username)
    else:
        #User authentication failed
        return HttpResponse('No user registered with: username: ' + username + ' and password: ' + password)

@login_required
def doLogout(request):
    logout(request)
    return render(request, 'IrrigationApp/pages/login.html', { 'userStatus':"USER LOGGED OUT" })

def showLogin(request):
    try:
        redirect=request.GET['next']
        return render(request, 'IrrigationApp/pages/login.html', {'redirect':redirect})
    except:    
        return render(request, 'IrrigationApp/pages/login.html', {})

def showRegistration(request):
    return render(request, 'IrrigationApp/pages/register.html', {})
        
def doRegistration(request):
    username = request.POST['username']
    password = request.POST['password']
    password_check = request.POST['password_check']
    email = request.POST['email']
    fullname = request.POST['fullname']
    ip_address = request.POST['ip_address']
    port_number = request.POST['port_number']
    
    if password != password_check:
        return HttpResponse('Passwords do not match: ' + password + ' != ' + password_check)                       
    else:
            try:
                oldUser = User.objects.get(username=username)
                return HttpResponse('User ' + username + ' already registered.' );
            except User.DoesNotExist:
                user = User.objects.create_user(username, email, password)
                user.save()
                userProfile = UserProfile(
                    user = user,
                    fullname = fullname,
                    ip_address = ip_address,
                    port = port_number
                            )
                userProfile.save()
                return redirect('/showLogin')

@login_required
def showAddNewSegment(request):
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
    
    return render(request, 'IrrigationApp/pages/addNewSegment.html', {'sensors':sensors, 'switches':switches})
    
@login_required
def doAddNewSegment(request):
    
    name = request.POST['name']
    sensor = request.POST['sensor']
    switch = request.POST['switch']
    moisture_minLimit = request.POST['moisture_minLimit']
    moisture_maxLimit = request.POST['moisture_maxLimit']
    duration_maxLimit = request.POST['duration_maxLimit']
    type = request.POST['type']
    if 'checkboxes' not in request.POST:
        enabled = False
    else:
        enabled = True
    
    sensor_list = list(Sensor.objects.all().filter(pinNumber=sensor))
    switch_list = list(Switch.objects.all().filter(pinNumber=switch))
    
    mSegment = Segment(
                    name = name,
                    sensor = sensor_list[0],
                    switch = switch_list[0],
                    moisture_minLimit = moisture_minLimit,
                    moisture_maxLimit = moisture_maxLimit,
                    duration_maxLimit = duration_maxLimit,
                    forecast_enabled = enabled,
                    type = type
                            )
    mSegment.save()
    return HttpResponse('Segment has been added succesfully!  Sensor: ' + sensor_list[0].pinNumber + 'Switch: ' + switch_list[0].pinNumber);

@login_required
def getSystemStatus(request):
    
    currentWeather = WeatherHistory.objects.all().order_by('-observation_time')[:1]
    segments = Segment.objects.all()
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    
    if 'pinNumber' in request.POST :
        pinNumber = request.POST['pinNumber']
        status = request.POST['status']
        mSwitch = Switch.objects.get(pinNumber=pinNumber)
        mSwitch.status = status
        mSwitch.save(update_fields=['status'])
        r = requests.get("http://192.168.0.105:80/?pinNumber="+ pinNumber +"&status="+ status)      
    
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'weathers':currentWeather, 'segments':segments, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules})


@login_required
def showSimpleSchedule(request):
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/simpleSchedule.html', { 'segments':segments})
    
@login_required
def doSimpleSchedule(request):
    
    name = request.POST['name']
    date = request.POST['date']
    time = request.POST['time']
    duration = request.POST['duration']
    if 'enabled_checkbox' not in request.POST:
        enabled = False
    else:
        enabled = True
    
    segments = Segment.objects.all()
    for segment in segments :    
        if str(segment.id) in request.POST:    
            mSimpleSchedule = SimpleSchedule(
                                             name=name,
                                             enabled=enabled,
                                             date=date,
                                             time=time,
                                             duration=duration,
                                             segment=segment)
            mSimpleSchedule.save()
    
    return HttpResponse('Schedule added succesfully!')

@login_required
def showRepeatableSchedule(request):
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/repeatableSchedule.html', { 'segments':segments})
    
@login_required
def doRepeatableSchedule(request):
    
    name = request.POST['name']
    time = request.POST['time']
    duration = request.POST['duration']
    if 'enabled_checkbox' not in request.POST:
        enabled = False
    else:
        enabled = True
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    segments = Segment.objects.all()
    for segment in segments :    
        if str(segment.id) in request.POST:    
            for day in days :
                if day in request.POST:
                    mRepeatableSchedule = RepeatableSchedule(
                                                     name=name,
                                                     enabled=enabled,
                                                     day=day,
                                                     time=time,
                                                     duration=duration,
                                                     segment=segment)
                    mRepeatableSchedule.save()
    
    return HttpResponse('Schedule added succesfully!')

@login_required
def deleteSimpleSchedule(request):
    
    id = request.POST['simpleSchedule']
    SimpleSchedule.objects.get(id=id).delete()
        
    return HttpResponse('Schedule deleted succesfully!')

@login_required
def deleteRepeatableSchedule(request):
    
    id = request.POST['repeatableSchedule']
    RepeatableSchedule.objects.get(id=id).delete()
        
    return HttpResponse('Schedule deleted succesfully!')