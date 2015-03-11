from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time
from django.contrib.auth.models import User
import codecs
import json

from IrrigationApp.models import IrrigationTemplate, IrrigationTemplateValue, IrrigationSettings, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Segment, Switch, Sensor, IrrigationHistory, Arduino, SoilType, TaskQueue

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from urllib.request import urlopen

import subprocess

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
    irrigationTemplates = IrrigationTemplate.objects.all()
    soilTypes = SoilType.objects.all()
    
    return render(request, 'IrrigationApp/pages/addNewSegment.html', { 'username':user.username, 'settings':settings, 'sensors':sensors, 'switches':switches, 'irrigationTemplates':irrigationTemplates, 'soilTypes':soilTypes })
    
@login_required
def doAddNewSegment(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    
    name = request.POST['name']
    size = request.POST['size']
    sensor = request.POST['sensor']
    switch = request.POST['switch']
    moisture_minLimit = request.POST['moisture_minLimit']
    moisture_maxLimit = request.POST['moisture_maxLimit']
    duration_maxLimit = request.POST['duration_maxLimit']
    irrigationTemplate_id = request.POST['irrigationTemplate']
    soil_type = request.POST['soil_type']
    type = request.POST['type']
    if 'checkboxes' not in request.POST:
        enabled = False
    else:
        enabled = True
        
    if irrigationTemplate_id=="None":
        irrigationTemplate=None
    else:
        irrigationTemplate = IrrigationTemplate.objects.get(id=irrigationTemplate_id)
        irrigationTemplate.day_counter=0
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    soil = SoilType.objects.get(id=soil_type)
    
    mSegment = Segment(
                    name = name,
                    sensor = sensor,
                    switch = switch,
                    moisture_minLimit = moisture_minLimit,
                    moisture_maxLimit = moisture_maxLimit,
                    duration_maxLimit = duration_maxLimit,
                    forecast_enabled = enabled,
                    type = type,
                    template = irrigationTemplate,
                    soil_type=soil,
                    size_m2=size
                            )
    mSegment.save()
    
    if irrigationTemplate is not None :
        irrigationTemplate.segment_id=mSegment
        irrigationTemplate.save(update_fields=['day_counter','segment_id'])
    
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
    irrigationTemplates = IrrigationTemplate.objects.all()
    soilTypes = SoilType.objects.all()
        
    return render(request, 'IrrigationApp/pages/editSegment.html', { 'username':user.username, 'settings':settings, 'segment':segment, 'sensors':sensors, 'switches':switches, 'irrigationTemplates':irrigationTemplates, 'soilTypes':soilTypes })

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
    size = request.POST['size']
    sensor = request.POST['sensor']
    switch = request.POST['switch']
    moisture_minLimit = request.POST['moisture_minLimit']
    moisture_maxLimit = request.POST['moisture_maxLimit']
    duration_maxLimit = request.POST['duration_maxLimit']
    irrigationTemplate_id = request.POST['irrigationTemplate']
    soil_type = request.POST['soil_type']
    type = request.POST['type']
    if 'checkboxes' not in request.POST:
        enabled = False
    else:
        enabled = True
    
    mSegment = Segment.objects.get(id=id)
        
    if irrigationTemplate_id=="None":
        irrigationTemplate=None
    else:
        irrigationTemplate = IrrigationTemplate.objects.get(id=irrigationTemplate_id)
        irrigationTemplate.day_counter=0
        irrigationTemplate.save(update_fields=['day_counter'])
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    soil = SoilType.objects.get(id=soil_type)
       
    mSegment.name = name
    mSegment.sensor = sensor
    mSegment.switch = switch
    mSegment.moisture_minLimit = moisture_minLimit
    mSegment.moisture_maxLimit = moisture_maxLimit
    mSegment.duration_maxLimit = duration_maxLimit
    mSegment.forecast_enabled = enabled
    mSegment.template = irrigationTemplate
    mSegment.type = type
    mSegment.soil_type=soil
    mSegment.size_m2=size
    mSegment.save()
    
    return redirect('/getSystemStatus')

def setIrrigation(mSegment, status, settings, arduino):
    mSwitch = Switch.objects.get(pinNumber=mSegment.switch.pinNumber)
    mSwitch.status = status
    mSwitch.save(update_fields=['status'])
    mSegment.switch=mSwitch
    mSegment.save(update_fields=['switch','up_time','irrigation_history']) 
    urlopen("http://"+arduino.IP+":"+arduino.PORT+"/pinNumber/"+mSwitch.pinNumber+"/status/"+str(mSwitch.status))
        
    switches = Switch.objects.all()
    running_segments=0;
    pump_status = False
    for switch in switches :
        if switch.pinNumber != settings.pump.pinNumber :
            if switch.status == 1 :
                running_segments=running_segments+1
                pump_status = True
        
    pump= Switch.objects.get(pinNumber=settings.pump.pinNumber)
    if pump_status :
        pump.status = 1
    else :
        pump.status = 0
    pump.save(update_fields=['status'])
    settings.pump=pump
    settings.running_segments=running_segments
    settings.save(update_fields=['pump','running_segments'])
    urlopen("http://"+arduino.IP+":"+arduino.PORT+"/pinNumber/"+pump.pinNumber+"/status/"+str(pump.status))

def addTaskToQueue(mSegment, settings, arduino):
    tasks = TaskQueue.objects.all().order_by('seq_number')
    TaskQueue(segment_id=mSegment,
                          seq_number=len(tasks)+1).save()
    if len(tasks) < settings.runnable_segments_number :
        switchIrrigation(mSegment,1,settings,arduino)
        
def deleteTaskFromQueue(mSegment, settings, arduino):
    if mSegment.switch.status == 1:
        tasks = TaskQueue.objects.all().order_by('seq_number')
        if len(tasks) > 0 :
            deleted_task=TaskQueue.objects.get(segment_id=mSegment)
            seq_number=deleted_task.seq_number
            deleted_task.delete()
            switchIrrigation(mSegment, 0, settings, arduino)
            tasks = TaskQueue.objects.all().order_by('seq_number')
            if tasks is not None:
                for task in tasks :
                    if task.seq_number>seq_number:
                        temp=TaskQueue.objects.get(segment_id=task.segment_id)
                        temp.seq_number=temp.seq_number-1
                        temp.save()
        else :
            switchIrrigation(mSegment, 0, settings, arduino)
    
def switchIrrigation(mSegment, status, settings, arduino):
    
    if status == 1 :
        if mSegment.switch.status == 0 and mSegment.duration_today<mSegment.duration_maxLimit :
            if mSegment.irrigation_history is None :
                mIrrigationHistory = IrrigationHistory(segment_id=mSegment,
                                                                   moisture_startValue=mSegment.sensor.value
                                                                   )
                mIrrigationHistory.save()
                mSegment.irrigation_history=mIrrigationHistory
            setIrrigation(mSegment, 1, settings, arduino)
                
    else :                
        if mSegment.switch.status == 1:
            if mSegment.irrigation_history is not None:
                mHistory=IrrigationHistory.objects.get(id=mSegment.irrigation_history.id)
                mHistory.end_date=datetime.now()
                mHistory.duration=mSegment.up_time+1
                mHistory.moisture_endValue=mSegment.sensor.value
                mHistory.status='done'
                mHistory.save(update_fields=['end_date','duration','moisture_endValue','status'])
                mSegment.up_time = 0
                mSegment.irrigation_history=None
            setIrrigation(mSegment, 0, settings, arduino)
        
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
        if status == '1':    
            addTaskToQueue(mSegment, settings, arduino)
        else :
            deleteTaskFromQueue(mSegment,settings, arduino)
    
    segments = Segment.objects.all()
    tasks = TaskQueue.objects.all().order_by('seq_number')
    
    pipe = subprocess.Popen(['/home/pi/tmp/test'], stdout=subprocess.PIPE)
    result = pipe.stdout.read()
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'result':result, 'username':user.username, 'arduino':arduino, 'settings':settings,'segments':segments, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules, 'tasks':tasks})


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
def deleteTask(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    id = request.POST['task']
    TaskQueue.objects.get(id=id).delete()
        
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
    evapotranspiracy = request.POST['evapotranspiracy']
    cost = request.POST['cost']
    number_of_runnable_segments = request.POST['number_of_runnable_segments']
    
    
    switch = Switch.objects.get(pinNumber=switch)
    settings = IrrigationSettings(id=0,
                                  pump=switch,
                                  evapotranspiracy=evapotranspiracy,
                                  cost_perLiter=cost,
                                  runnable_segments_number=number_of_runnable_segments)
    
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
    
    for digital in js['digitals'] :
        Switch(pinNumber=digital['pinNumber'],status=digital['status']).save()
    
    for node in js['nodes'] :
        Sensor(node=node['nodeId'],value=node['value']).save()
    
    
    return redirect('/showAddSettings')

@login_required
def showAddSoilType(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
        
    return render(request, 'IrrigationApp/pages/addSoilType.html', { 'username':user.username })

@login_required
def doAddSoilType(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')

    name = request.POST['name']
    value = request.POST['value']

    SoilType(name=name,value=value).save();
    
    return redirect('/getSystemStatus')

def showAddIrrigationTemplate(request):
    
    return render(request, 'IrrigationApp/pages/addIrrigationTemplate.html', { })

def doAddIrrigationTemplate(request):
    
    name = request.POST['name']
    series = request.POST['series']
    js = json.loads(series)
    irrigationTemplate = IrrigationTemplate(name=name,
                                            day_counter=0)
    irrigationTemplate.save()
    
    for point in js['data'] :    
        IrrigationTemplateValue(template=irrigationTemplate,
                             day_number=point['x'],
                             value=point['y']).save()                                                   
    
    irrigationTemplateValues = IrrigationTemplateValue.objects.filter(template=irrigationTemplate)
    return redirect('/getSystemStatus')

def showDeleteIrrigationTemplate(request):
    
    irrigationTemplates = IrrigationTemplate.objects.all()
    
    return render(request, 'IrrigationApp/pages/deleteIrrigationTemplate.html', { 'irrigationTemplates':irrigationTemplates })

def doDeleteIrrigationTemplate(request):
    id = request.POST['irrigationTemplate']
    
    irrigationTemplate = IrrigationTemplate.objects.get(id=id)
    IrrigationTemplateValue.objects.filter(template=irrigationTemplate).delete()
    irrigationTemplate.delete()
    
    return redirect('/getSystemStatus')

def showIrrigationTemplateValues(request):
    id = request.GET['template']
    irrigationTemplate = IrrigationTemplate.objects.get(id=id)
    irrigationTemplateValues = IrrigationTemplateValue.objects.filter(template=irrigationTemplate)
    
    return render(request, 'IrrigationApp/pages/irrigationTemplateValues.html', { 'irrigationTemplate':irrigationTemplate, 'irrigationTemplateValues':irrigationTemplateValues })


def showAddIrrigationTemplate2(request):
    
    return render(request, 'IrrigationApp/pages/addIrrigationTemplate2.html', { })