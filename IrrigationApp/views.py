from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time
from django.contrib.auth.models import User
import codecs
import json

from IrrigationApp.models import IrrigationTemplate, IrrigationTemplateValue, IrrigationSettings, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Segment, Switch, Sensor, IrrigationHistory, Arduino

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
        request.session['username']=username
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
    
    if password != password_check:
        return HttpResponse('Passwords do not match: ' + password + ' != ' + password_check)                       
    else:
            try:
                oldUser = User.objects.get(username=username)
                return HttpResponse('User ' + username + ' already registered.' );
            except User.DoesNotExist:
                user = User.objects.create_user(username, email, password)
                user.save()
                
    return redirect('/showLogin')

@login_required
def showAddNewSegment(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
    
    return render(request, 'IrrigationApp/pages/addNewSegment.html', { 'username':user.username, 'settings':settings, 'sensors':sensors, 'switches':switches})
    
@login_required
def doAddNewSegment(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    
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
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    arduino = Arduino.objects.all()
    if arduino.exists() :
        arduino = Arduino.objects.get(id=0)
    else:
        return redirect('/showAddArduino')
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    
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
            if mSegment.irrigation_history is not None:
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
        urlopen("http://"+arduino.IP+":"+arduino.PORT+"/?pinNumber="+mSwitch.pinNumber+"&status="+mSwitch.status)
    
        switches = Switch.objects.all()
        pump_status = False
        for switch in switches :
            if switch.pinNumber != settings.pump.pinNumber :
                if switch.status == 'on' :
                    pump_status = True
        
        pump= Switch.objects.get(pinNumber=settings.pump.pinNumber)
        if pump_status :
            pump.status = "on"
        else :
            pump.status = "off"
        pump.save(update_fields=['status'])
        settings.pump=pump
        settings.save(update_fields=['pump'])
        urlopen("http://"+arduino.IP+":"+arduino.PORT+"/?pinNumber="+pump.pinNumber+"&status="+pump.status)
    
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'username':user.username, 'arduino':arduino, 'settings':settings,'segments':segments, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules})


@login_required
def showSimpleSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/simpleSchedule.html', { 'username':user.username, 'settings':settings, 'segments':segments})
    
@login_required
def doSimpleSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
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
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')

    settings = IrrigationSettings.objects.get(id=0)
    segments = Segment.objects.all()
    return render(request, 'IrrigationApp/pages/repeatableSchedule.html', { 'username':user.username, 'settings':settings, 'segments':segments})
    
@login_required
def doRepeatableSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')

    settings = IrrigationSettings.objects.get(id=0)
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
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    id = request.POST['simpleSchedule']
    SimpleSchedule.objects.get(id=id).delete()
        
    return redirect('/getSystemStatus')

@login_required
def deleteRepeatableSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    id = request.POST['repeatableSchedule']
    RepeatableSchedule.objects.get(id=id).delete()
        
    return redirect('/getSystemStatus')

@login_required
def showEditSegment(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    id = request.POST['editSegment']
    segment = Segment.objects.get(id=id)
    
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
        
    return render(request, 'IrrigationApp/pages/editSegment.html', { 'username':user.username, 'settings':settings, 'segment':segment, 'sensors':sensors, 'switches':switches })

@login_required
def doEditSegment(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
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
    
    sensor = Sensor.objects.get(pinNumber=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    
    mSegment = Segment(
                    id = id,
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
def showWeatherStatus(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    currentWeather = WeatherHistory.objects.all().order_by('-observation_time')[:1]
    weatherForecasts = WeatherForecast.objects.all()
        
    return render(request, 'IrrigationApp/pages/weatherStatus.html', { 'username':user.username, 'settings':settings, 'weathers':currentWeather, 'weatherForecasts':weatherForecasts })

@login_required
def showIrrigationHistory(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/history.html', { 'username':user.username, 'settings':settings, 'irrigationHistories':irrigationHistories })

@login_required
def showAddSettings(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    switches = Switch.objects.all()
        
    return render(request, 'IrrigationApp/pages/addSettings.html', { 'username':user.username, 'switches':switches })

@login_required
def doAddSettings(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    switch = request.POST['switch']
    
    switch = Switch.objects.get(pinNumber=switch)
    settings = IrrigationSettings(id=0,
                                  pump=switch)
    settings.save()
    
    return redirect('/getSystemStatus')

@login_required
def showAddArduino(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
        
    return render(request, 'IrrigationApp/pages/addArduino.html', { 'username':user.username })

@login_required
def doAddArduino(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')

    ip = request.POST['ip_address']
    port = request.POST['port_number']

    arduino = Arduino(id=0,
                      IP=ip,
                      PORT=port)
    arduino.save()

    res = urlopen('http://'+arduino.IP+':'+arduino.PORT)
    reader = codecs.getreader("utf-8")
    js = json.load(reader(res))
    
    d01_status=js['digital']['D1'];
    d02_status=js['digital']['D2'];
    d03_status=js['digital']['D3'];
    d04_status=js['digital']['D4'];
    
    a01_status=js['analog']['A1'];
    a02_status=js['analog']['A2'];
    a03_status=js['analog']['A3'];
    a04_status=js['analog']['A4'];
    
    mSensor1 = Sensor(
        pinNumber='a1',
        status=a01_status)
    mSensor1.save()
    
    mSensor2 = Sensor(
        pinNumber='a2',
        status=a02_status)
    mSensor2.save()
    
    mSensor3 = Sensor(
        pinNumber='a3',
        status=a03_status)
    mSensor3.save()
    
    mSensor4 = Sensor(
        pinNumber='a4',
        status=a04_status)
    mSensor4.save()
    
    mSwitch1 = Switch(
        pinNumber='d1',
        status=d01_status)
    mSwitch1.save()
    
    mSwitch2 = Switch(
        pinNumber='d2',
        status=d02_status)
    mSwitch2.save()
    
    mSwitch3 = Switch(
        pinNumber='d3',
        status=d03_status)
    mSwitch3.save()
    
    mSwitch4 = Switch(
        pinNumber='d4',
        status=d04_status)
    mSwitch4.save()
    
    return redirect('/showAddSettings')


def showMoistureChart(request):
    
    return render(request, 'IrrigationApp/charts/moisture.html', { })

def showAddIrrigationTemplate(request):
    segments = Segment.objects.all()
    
    return render(request, 'IrrigationApp/pages/addIrrigationTemplate.html', { 'segments':segments })

def doAddIrrigationTemplate(request):
    
    segment_id = request.POST['segment']
    name = request.POST['name']
    
    segment=Segment.objects.get(id=segment_id)
    
    irrigationTemplate = IrrigationTemplate(name=name,
                                            segment=segment)
    irrigationTemplate.save()
    
    return HttpResponse('IrrigationTemplate saved: (id:' + segment_id + ', name:' + name);

def doAddIrrigationTemplateValues(request):
    
    irrigationTemplate = IrrigationTemplate.objects.get(id=0)
    IrrigationTemplateValues(template=irrigationTemplate,
                             day_number=0,
                             value=500).save()
    IrrigationTemplateValues(template=irrigationTemplate,
                             day_number=1,
                             value=800).save()
    IrrigationTemplateValues(template=irrigationTemplate,
                             day_number=2,
                             value=400).save()
    IrrigationTemplateValues(template=irrigationTemplate,
                             day_number=3,
                             value=600).save()                                                                           
    
    return HttpResponse('IrrigationTemplateValues saved');
