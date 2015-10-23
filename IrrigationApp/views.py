from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time
from django.contrib.auth.models import User
import codecs
import json
import logging
import time

from IrrigationApp.models import Pump, IrrigationTemplate, ZoneTemplateValue, KcValue, IrrigationSettings, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Zone, Switch, Sensor, IrrigationHistory, SoilType, TaskQueue

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
def showAddNewZone(request):
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
    
    return render(request, 'IrrigationApp/pages/addNewZone.html', { 'username':user.username, 'settings':settings, 'sensors':sensors, 'switches':switches, 'irrigationTemplates':irrigationTemplates, 'soilTypes':soilTypes })
    
@login_required
def doAddNewZone(request):
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
    root = request.POST['root']
    deviation = request.POST['deviation']
    efficiency = request.POST['efficiency']
    if 'checkboxes' not in request.POST:
        enabled = False
    else:
        enabled = True
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    soil = SoilType.objects.get(id=soil_type)
    
    zone = Zone(name = name,
         sensor = sensor,
         switch = switch,
         moisture_minLimit = moisture_minLimit,
         moisture_maxLimit = moisture_maxLimit,
         duration_maxLimit = duration_maxLimit,
         forecast_enabled = enabled,
         type = type,
         soil_type=soil,
         size_m2=size,
         root=root,
         moisture_deviation=deviation,
         efficiency=efficiency)
    zone.save()
    
    if irrigationTemplate_id!="None":
        irrigationTemplate = IrrigationTemplate.objects.get(id=irrigationTemplate_id)
        setZoneTemplate(zone,irrigationTemplate)
    
    return redirect('/getSystemStatus')

@login_required
def showEditZone(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    id = request.POST['editZone']
    zone = Zone.objects.get(id=id)
    
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
    irrigationTemplates = IrrigationTemplate.objects.all()
    soilTypes = SoilType.objects.all()
        
    return render(request, 'IrrigationApp/pages/editZone.html', { 'username':user.username, 'settings':settings, 'zone':zone, 'sensors':sensors, 'switches':switches, 'irrigationTemplates':irrigationTemplates, 'soilTypes':soilTypes })

@login_required
def doEditZone(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    id = request.POST['zone_id']
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
    root = request.POST['root']
    deviation = request.POST['deviation']
    efficiency = request.POST['efficiency']
    if 'checkboxes' not in request.POST:
        enabled = False
    else:
        enabled = True
    
    zone = Zone.objects.get(id=id)        
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    soil = SoilType.objects.get(id=soil_type)
       
    zone.name = name
    zone.sensor = sensor
    zone.switch = switch
    zone.moisture_minLimit = moisture_minLimit
    zone.moisture_maxLimit = moisture_maxLimit
    zone.duration_maxLimit = duration_maxLimit
    zone.forecast_enabled = enabled
    zone.type = type
    zone.soil_type=soil
    zone.size_m2=size
    zone.root=root
    zone.moisture_deviation=deviation
    zone.efficiency=efficiency
    zone.save()
    
    if irrigationTemplate_id!="None":
        irrigationTemplate = IrrigationTemplate.objects.get(id=irrigationTemplate_id)
        setZoneTemplate(zone,irrigationTemplate)
    
    return redirect('/getSystemStatus')


def setZoneTemplate(zone,irrigationTemplate):
    settings = IrrigationSettings.objects.get(id=0)
    settings.water
    settings.evapotranspiracy
    
    template_values = KcValue.objects.filter(template=irrigationTemplate)
    pr=settings.water/zone.size_m2*60/25.4
    gyz=zone.root_length/30
    
    skipped_day=0
    for template_value in template_values :    
        
        day_number=template_value.day_number
        kc_value=template_value.kc_value
        
        f=gyz*zone.moisture_deviation/100/(settings.evapotranspiracy*kc_value)
        rt=60*f*settings.evapotranspiracy*kc_value/(pr*zone.efficiency/100)
        mm=rt*0.207
        
        if skipped_day==0 :
            ZoneTemplateValue(zone=zone,
                              kc_value=template_value,
                              irrigation_required=True,
                              runtime=int(rt),
                              water_mm=mm).save()
            skipped_day=int(f)-1 
        else :
            ZoneTemplateValue(zone=zone,
                              kc_value=template_value,
                              irrigation_required=False,
                              runtime=0,
                              water_mm=0).save()
        
        skipped_day=skipped_day-1
    
    zone.template=irrigationTemplate
    zone.save(update_fields=['template'])
    return

def setIrrigation(mZone, status):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    
    mSwitch = Switch.objects.get(pinNumber=mZone.switch.pinNumber)
    mSwitch.status = status
    mSwitch.save(update_fields=['status'])
    mZone.switch=mSwitch
    mZone.save(update_fields=['switch','up_time','irrigation_history']) 
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(mSwitch.pinNumber), str(mSwitch.status)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)       
    switches = Switch.objects.all()
    running_zones=0;
    pump_status = False
    pump=Pump.objects.get(id=0)
    
    for switch in switches :
        if switch.pinNumber != pump.switch.pinNumber :
            if switch.status == 1 :
                running_zones=running_zones+1
                pump_status = True
        
    if pump_status :
        pump.switch.status = 1
    else :
        pump.switch.status = 0
    pump.save()
    settings.running_zones=running_zones
    settings.save(update_fields=['running_zones'])
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(pump.switch.pinNumber), str(pump.switch.status)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return
    
def addTaskToQueue(mZone):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
    tasks = TaskQueue.objects.all().order_by('seq_number')
    if len(tasks) < settings.runnable_zones_number :
        switchIrrigation(mZone,1)
    else :
        TaskQueue(zone_id=mZone,seq_number=len(tasks)+1).save()
        
def deleteTaskFromQueue(mZone):
    if mZone.switch.status == 1:
        tasks = TaskQueue.objects.all().order_by('seq_number')
        if len(tasks) > 0 :
            deleted_task=TaskQueue.objects.get(zone_id=mZone)
            seq_number=deleted_task.seq_number
            deleted_task.delete()
            switchIrrigation(mZone, 0)
            tasks = TaskQueue.objects.all().order_by('seq_number')
            if tasks is not None:
                for task in tasks :
                    if task.seq_number>seq_number:
                        temp=TaskQueue.objects.get(zone_id=task.zone_id)
                        temp.seq_number=temp.seq_number-1
                        temp.save()
        else :
            switchIrrigation(mZone, 0)
    
def switchIrrigation(mZone, status):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    
    pump=Pump.objects.get(id=0)
    
    if status == 1 :
        if pump.switch.status == 1 or pump.down_time >= pump.stop_limit :
            if mZone.switch.status == 0 and mZone.duration_today<mZone.duration_maxLimit :
                if mZone.irrigation_history is None :
                    mIrrigationHistory = IrrigationHistory(zone_id=mZone,
                                                                       moisture_startValue=mZone.sensor.value
                                                                       )
                    mIrrigationHistory.save()
                    mZone.irrigation_history=mIrrigationHistory
                
                result = setIrrigation(mZone, 1)
                return result
                
        else :
            return 'Waiting for pump'
                
    else :  
        if pump.switch.status == 0 or pump.up_time >= pump.run_limit:              
            if mZone.switch.status == 1:
                if mZone.irrigation_history is not None:
                    mHistory=IrrigationHistory.objects.get(id=mZone.irrigation_history.id)
                    mHistory.end_date=datetime.now()
                    mHistory.duration=mZone.up_time+1
                    mHistory.moisture_endValue=mZone.sensor.value
                    mHistory.status='done'
                    mHistory.save(update_fields=['end_date','duration','moisture_endValue','status'])
                    mZone.up_time = 0
                    mZone.irrigation_history=None
                
                result = setIrrigation(mZone, 0)
                return result
        else :
            return 'Waiting for pump'
        
@login_required
def getSystemStatus(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    
    result='N/A'
    
    if 'zone' in request.POST :
        zone = request.POST['zone']
        status = request.POST['status']
        mZone = Zone.objects.get(id=zone)
        if status == '1':    
            addTaskToQueue(mZone)
        else :
            deleteTaskFromQueue(mZone)
    
    zones = Zone.objects.all()
    tasks = TaskQueue.objects.all().order_by('seq_number')
    pump = Pump.objects.get(id=0)
    
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'pump':pump, 'username':user.username, 'settings':settings,'zones':zones, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules, 'tasks':tasks})


@login_required
def showSimpleSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    settings = IrrigationSettings.objects.get(id=0)
    zones = Zone.objects.all()
    return render(request, 'IrrigationApp/pages/simpleSchedule.html', { 'username':user.username, 'settings':settings, 'zones':zones})
    
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
    zones = Zone.objects.all()
    for zone in zones :    
        if str(zone.id) in request.POST:    
            mSimpleSchedule = SimpleSchedule(
                                             date=date,
                                             time=time,
                                             duration=duration,
                                             zone=zone)
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
    zones = Zone.objects.all()
    return render(request, 'IrrigationApp/pages/repeatableSchedule.html', { 'username':user.username, 'settings':settings, 'zones':zones})
    
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
    zones = Zone.objects.all()
    for zone in zones :    
        if str(zone.id) in request.POST:    
            for day in days :
                if day in request.POST:
                    mRepeatableSchedule = RepeatableSchedule(
                                                     name=name,
                                                     day=day,
                                                     time=time,
                                                     duration=duration,
                                                     zone=zone)
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
    
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/history.html', { 'username':user.username, 'irrigationHistories':irrigationHistories })

@login_required
def deleteIrrigationHistory(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    
    IrrigationHistory.objects.all().delete()
    
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/history.html', { 'username':user.username, 'irrigationHistories':irrigationHistories })

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
    number_of_runnable_zones = request.POST['number_of_runnable_zones']
    run_limit = request.POST['run_limit']
    stop_limit = request.POST['stop_limit']
    
    switch = Switch.objects.get(pinNumber=switch)
    settings = IrrigationSettings(id=0,
                                  evapotranspiracy=evapotranspiracy,
                                  cost_perLiter=cost,
                                  runnable_zones_number=number_of_runnable_zones)
    settings.save()
    settings.save()
    pump = Pump(id=0,
                switch=switch,
                run_limit=run_limit,
                stop_limit=stop_limit)
    pump.save()
    
    return redirect('/getSystemStatus')

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

def doAddIrrigationTemplate(request):
    
    name = request.POST['name']
    series = request.POST['series']
    
    js = json.loads(series)
    
    template = IrrigationTemplate(name).save()
    
    settings = IrrigationSettings.objects.get(id=0)
    settings.water
    settings.evapotranspiracy
    
    zone = Zone.objects.get(id=zone_id)
    zone.size_m2
    zone.root_length
    zone.moisture_deviation
    zone.efficiency
    
    pr=settings.water/zone.size_m2*60/25.4
    gyz=zone.root_length/30
    
    skipped_day=0
    for point in js['data'] :    
        day_number=point['x']
        kc_value=point['y']
        
        KcValues(template,day_number,kc_value).save()
        
        f=gyz*zone.moisture_deviation/100/(settings.evapotranspiracy*kc_value)
        rt=60*f*settings.evapotranspiracy*kc_value/(pr*zone.efficiency/100)
        mm=rt*0.207
        
        if skipped_day==0 :
            IrrigationTemplateValue(template=irrigationTemplate,
                             day_number=day_number,
                             kc_value=kc_value,
                             irrigation_required=True,
                             runtime=int(rt),
                             water_mm=mm).save()  
            skipped_day=int(f)-1 
        else :
            IrrigationTemplateValue(template=irrigationTemplate,
                             day_number=day_number,
                             kc_value=kc_value,
                             irrigation_required=False,
                             runtime=0,
                             water_mm=0).save()
        
        skipped_day=skipped_day-1
                                                            
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

def showZoneTemplate(request):
    zone_id = request.GET['zone']
    zone = Zone.objects.get(id=zone_id)
    
    template_values = ZoneTemplateValue.objects.filter(zone=zone)
    
    return render(request, 'IrrigationApp/pages/templateStatus.html', { 'template_values':template_values, 'zone':zone })

def showAddIrrigationTemplate(request):
    return render(request, 'IrrigationApp/pages/addIrrigationTemplate.html', { })