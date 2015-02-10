from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time

from IrrigationApp.models import UserProfile, IrrigationSettings, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Segment, Switch, Sensor, IrrigationHistory

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from urllib.request import urlopen

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
    switches = Switch.objects.all()
    
    return render(request, 'IrrigationApp/pages/register.html', {'switches':switches})
        
def doRegistration(request):
    username = request.POST['username']
    password = request.POST['password']
    password_check = request.POST['password_check']
    email = request.POST['email']
    fullname = request.POST['fullname']
    ip_address = request.POST['ip_address']
    port_number = request.POST['port_number']
    switch = request.POST['switch']
    
    switch = Switch.objects.get(pinNumber=switch)
    
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
                    fullname = fullname
                            )
                userProfile.save()
                
                mIrrigationSettings = IrrigationSettings(user_profile=userProfile,
                                                         arduino_IP=ip_address,
                                                         arduino_PORT=port_number,
                                                         pump=switch)
                mIrrigationSettings.save()
                
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
    
    sensor = Sensor.objects.get(pinNumber=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    
    mSegment = Segment(
                    name = name,
                    sensor = sensor,
                    switch = switch,
                    moisture_minLimit = moisture_minLimit,
                    moisture_maxLimit = moisture_maxLimit,
                    duration_maxLimit = duration_maxLimit,
                    forecast_enabled = enabled,
                    type = type
                            )
    mSegment.save()
    return redirect('/getSystemStatus')

@login_required
def getSystemStatus(request):
    
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    settings = IrrigationSettings.objects.all()[:1]
    
    if 'segment' in request.POST :
        segment = request.POST['segment']
        status = request.POST['status']
        mSegment = Segment.objects.get(id=segment)
        if status == 'on' :
            mSegment.up_time = mSegment.up_time
            mIrrigationHistory = IrrigationHistory(segment_id=mSegment,
                                                   moisture_startValue=mSegment.sensor.status
                                                   )
            mIrrigationHistory.save()
            mSegment.irrigation_history=mIrrigationHistory
        else :
            mHistory=IrrigationHistory.objects.get(id=mSegment.irrigation_history.id)
            mHistory.end_date=datetime.now()
            mHistory.duration=mSegment.up_time+1
            mHistory.moisture_endValue=mSegment.sensor.status
            mHistory.status='done'
            mHistory.save(update_fields=['end_date','duration','moisture_endValue','status'])
            mSegment.up_time = 0
    
        mSwitch = Switch.objects.get(pinNumber=mSegment.switch.pinNumber)
        mSwitch.status = status
        mSwitch.save(update_fields=['status'])
        mSegment.switch=mSwitch
        mSegment.save(update_fields=['switch','up_time','irrigation_history']) 
        urlopen("http://192.168.0.105:80/?pinNumber="+mSwitch.pinNumber+"&status="+mSwitch.status)
    
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'settings':settings,'segments':segments, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules})


@login_required
def showSimpleSchedule(request):
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/simpleSchedule.html', { 'segments':segments})
    
@login_required
def doSimpleSchedule(request):
    
    date = request.POST['date']
    time = request.POST['time']
    duration = request.POST['duration']
    segments = Segment.objects.all()
    for segment in segments :    
        if str(segment.id) in request.POST:    
            mSimpleSchedule = SimpleSchedule(
                                             date=date,
                                             time=time,
                                             duration=duration,
                                             segment=segment)
            mSimpleSchedule.save()
    
    return redirect('/getSystemStatus')

@login_required
def showRepeatableSchedule(request):
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/repeatableSchedule.html', { 'segments':segments})
    
@login_required
def doRepeatableSchedule(request):
    
    name = request.POST['name']
    time = request.POST['time']
    duration = request.POST['duration']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    segments = Segment.objects.all()
    for segment in segments :    
        if str(segment.id) in request.POST:    
            for day in days :
                if day in request.POST:
                    mRepeatableSchedule = RepeatableSchedule(
                                                     name=name,
                                                     day=day,
                                                     time=time,
                                                     duration=duration,
                                                     segment=segment)
                    mRepeatableSchedule.save()
    
    return redirect('/getSystemStatus')

@login_required
def deleteSimpleSchedule(request):
    
    id = request.POST['simpleSchedule']
    SimpleSchedule.objects.get(id=id).delete()
        
    return redirect('/getSystemStatus')

@login_required
def deleteRepeatableSchedule(request):
    
    id = request.POST['repeatableSchedule']
    RepeatableSchedule.objects.get(id=id).delete()
        
    return redirect('/getSystemStatus')

@login_required
def showEditSegment(request):
    
    id = request.POST['editSegment']
    segment = Segment.objects.get(id=id)
    
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
        
    return render(request, 'IrrigationApp/pages/editSegment.html', { 'segment':segment, 'sensors':sensors, 'switches':switches })

@login_required
def doEditSegment(request):
    
    id = request.POST['segment_id']
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
                    id = id,
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
    return redirect('/getSystemStatus')

@login_required
def showWeatherStatus(request):
    
    currentWeather = WeatherHistory.objects.all().order_by('-observation_time')[:1]
    weatherForecasts = WeatherForecast.objects.all()
        
    return render(request, 'IrrigationApp/pages/weatherStatus.html', { 'weathers':currentWeather, 'weatherForecasts':weatherForecasts })

@login_required
def showIrrigationHistory(request):
    
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/history.html', { 'irrigationHistories':irrigationHistories })