from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time

from IrrigationApp.models import UserProfile
from IrrigationApp.models import WeatherHistory
from IrrigationApp.models import Segment
from IrrigationApp.models import Switch
from IrrigationApp.models import Sensor

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests


def test(request):
    return render(request, 'IrrigationApp/pages/test.html')

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
            return render(request, 'IrrigationApp/pages/main.html', { 'username':username })
        except:
            return HttpResponse('Error during login: ' + username)
    else:
        #User authentication failed
        return HttpResponse('Authentication failed ' + username + ' ' + password)

#@login_required
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
                return HttpResponse('User ' + username + ' registered successfully.' );

#@login_required
def showAddNewSegment(request):
    return render(request, 'IrrigationApp/pages/addNewSegment.html', {})
    
#@login_required
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

#@login_required
def getSystemStatus(request):
    
    if 'pinNumber' in request.POST :
        pinNumber = request.POST['pinNumber']
        status = request.POST['status']
        r = requests.get("http://192.168.0.105:80/?pinNumber="+ pinNumber +"&status="+ status)    
        #mSwitch = Switch(
         #   pinNumber=pinNumber,
          #  status=status)
        #mSwitch.save()      
    
    currentWeather = WeatherHistory.objects.all().order_by('-observation_time')[:1]
    
    segments = Segment.objects.all()
    
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'weathers':currentWeather, 'segments':segments})