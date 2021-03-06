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
import math
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from urllib2 import urlopen
from IrrigationApp.models import MoistureHistory, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Zone, Switch, Sensor, IrrigationHistory
from IrrigationApp.shared import setIrrigation, switchIrrigation, checkZone

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
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
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
    
    Switch(pinNumber="1",status=0).save()
    Switch(pinNumber="2",status=0).save()
    Sensor(node="2",value=0).save()                
    return redirect('/showLogin')

@login_required
def showAddNewZone(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()    
    return render(request, 'IrrigationApp/pages/addNewZone.html', { 'username':user.username, 'sensors':sensors, 'switches':switches })
    
@login_required
def doAddNewZone(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    name = request.POST['name']
    sensor = request.POST['sensor']
    switch = request.POST['switch']
    forecast_mm_limit = request.POST['forecast_mm_limit']
    current_pipe = request.POST['current_pipe']
    duration_maxLimit = request.POST['duration_maxLimit']
    if 'forecast' not in request.POST:
        forecast = False
    else:
        forecast = True
    if 'irrigation' not in request.POST:
        irrigation = False
    else:
        irrigation = True
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
    
    zone = Zone(name = name,
         sensor = sensor,
         switch = switch,
         forecast_mm_limit = forecast_mm_limit,
         current_pipe = current_pipe,
         duration_maxLimit = duration_maxLimit,
         forecast_enabled = forecast,
         irrigation_enabled = irrigation)
    zone.save()    
    return redirect('/getSystemStatus')

@login_required
def showEditZone(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    id = request.POST['editZone']
    zone = Zone.objects.get(id=id)
    
    sensors = Sensor.objects.all()
    switches = Switch.objects.all()
        
    return render(request, 'IrrigationApp/pages/editZone.html', { 'username':user.username, 'zone':zone, 'sensors':sensors, 'switches':switches })

@login_required
def doEditZone(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    id = request.POST['zone_id']
    name = request.POST['name']
    sensor = request.POST['sensor']
    switch = request.POST['switch']
    forecast_mm_limit = request.POST['forecast_mm_limit']
    current_pipe = request.POST['current_pipe']
    duration_maxLimit = request.POST['duration_maxLimit']
    if 'forecast' not in request.POST:
        forecast = False
    else:
        forecast = True
    if 'irrigation' not in request.POST:
        irrigation = False
    else:
        irrigation = True
    
    zone = Zone.objects.get(id=id)        
    
    sensor = Sensor.objects.get(node=sensor)
    switch = Switch.objects.get(pinNumber=switch)
       
    zone.name = name
    zone.sensor = sensor
    zone.switch = switch
    zone.forecast_mm_limit = forecast_mm_limit
    zone.current_pipe = current_pipe
    zone.duration_maxLimit = duration_maxLimit
    zone.forecast_enabled = forecast
    zone.irrigation_enabled = irrigation
    zone.save()
    
    return redirect('/getSystemStatus')

@login_required
def doCheckZone(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    id = request.POST['checkZone']
    mZone = Zone.objects.get(id=id)
    checkZone(mZone)    
    return redirect('/getSystemStatus')

@login_required
def getSystemStatus(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    if 'zone' in request.POST :
        zone = request.POST['zone']
        status = request.POST['status']
        mZone = Zone.objects.get(id=zone) 
        switchIrrigation(mZone, status)
                
    zones = Zone.objects.all()
    simpleSchedules = SimpleSchedule.objects.order_by('date', 'time')
    repeatableSchedules = RepeatableSchedule.objects.order_by('day', 'time')
    
    return render(request, 'IrrigationApp/pages/systemStatus.html', { 'username':user.username, 'zones':zones, 'simpleSchedules':simpleSchedules, 'repeatableSchedules':repeatableSchedules})

@login_required
def showSimpleSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    zones = Zone.objects.all()
    return render(request, 'IrrigationApp/pages/simpleSchedule.html', { 'username':user.username,'zones':zones})
    
@login_required
def doSimpleSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
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
    zones = Zone.objects.all()
    return render(request, 'IrrigationApp/pages/repeatableSchedule.html', { 'username':user.username, 'zones':zones})
    
@login_required
def doRepeatableSchedule(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    name = request.POST['name']
    time = request.POST['time']
    duration = request.POST['duration']
    days = ['1Monday', '2Tuesday', '3Wednesday', '4Thursday', '5Friday', '6Saturday', '7Sunday']
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
def deleteZone(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    id = request.POST['zone']
    Zone.objects.get(id=id).delete()
        
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
def showWeatherStatus(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    currentWeather = WeatherHistory.objects.all().order_by('-observation_time')[:1]
    weatherForecasts = WeatherForecast.objects.all()
        
    return render(request, 'IrrigationApp/pages/weatherStatus.html', { 'username':user.username, 'weathers':currentWeather, 'weatherForecasts':weatherForecasts })

@login_required
def showIrrigationHistory(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/irrigationHistory.html', { 'username':user.username, 'irrigationHistories':irrigationHistories })

@login_required
def showMoistureHistory(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    zone_id = request.POST['zone_id']
    zone=Zone.objects.get(id=zone_id)
    moistureHistories = MoistureHistory.objects.filter(zone_id=zone).order_by('-date')[:200][::-1]
        
    return render(request, 'IrrigationApp/pages/moistureHistory.html', { 'username':user.username, 'moistureHistories':moistureHistories, 'zone':zone })

@login_required
def showWeatherHistory(request):
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    weatherHistories = WeatherHistory.objects.all().order_by('-observation_time')[:72][::-1]
        
    return render(request, 'IrrigationApp/pages/weatherHistory.html', { 'username':user.username, 'weatherHistories':weatherHistories })

@login_required
def deleteIrrigationHistory(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    IrrigationHistory.objects.all().delete()
    
    irrigationHistories = IrrigationHistory.objects.all().order_by('-end_date')
        
    return render(request, 'IrrigationApp/pages/irrigationHistory.html', { 'username':user.username, 'irrigationHistories':irrigationHistories })

@login_required
def showAddSettings(request):        
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    return render(request, 'IrrigationApp/pages/addSettings.html', { 'username':user.username})

@login_required
def doAddSettings(request):    
    if request.session.get('username') :
        username = request.session.get('username')
        user = User.objects.get(username=username)
    else :
        return redirect('/showLogin')
    return redirect('/getSystemStatus')



#===============================================================================
# def setZoneTemplate(zone,irrigationTemplate):
#     settings = IrrigationSettings.objects.get(id=0)
#     
#     template_values = KcValue.objects.filter(template=irrigationTemplate)
#     pr=4.0/float(zone.size_m2)*60.0/25.4
#     gyz=float(zone.root_length)/30.0
#     
#     skipped_day=0
#     for template_value in template_values :    
#         
#         day_number=template_value.day_number
#         kc_value=template_value.kc_value
#         
#         f=(gyz*float(zone.moisture_deviation)/100.0)/(settings.evapotranspiracy*kc_value)
#         rt=(60.0*f*settings.evapotranspiracy*kc_value)/(pr*float(zone.efficiency)/100.0)
#         mm=rt*0.207
#         
#         if skipped_day==0 :
#             ZoneTemplateValue(zone=zone,
#                               kc_value=template_value,
#                               irrigation_required=True,
#                               runtime=int(round(rt,0)),
#                               water_mm=mm).save()
#             skipped_day=int(round(f,0)) 
#         else :
#             ZoneTemplateValue(zone=zone,
#                               kc_value=template_value,
#                               irrigation_required=False,
#                               runtime=0,
#                               water_mm=0).save()
#         
#         if skipped_day>0 :
#             skipped_day=skipped_day-1
#     
#     zone.irrigation_template=irrigationTemplate
#     zone.save(update_fields=['irrigation_template'])
#     return
#===============================================================================


#===============================================================================
# @login_required
# def showAddSoilType(request):
#     if request.session.get('username') :
#         username = request.session.get('username')
#         user = User.objects.get(username=username)
#     else :
#         return redirect('/showLogin')
#         
#     return render(request, 'IrrigationApp/pages/addSoilType.html', { 'username':user.username })
# 
# @login_required
# def doAddSoilType(request):
#     if request.session.get('username') :
#         username = request.session.get('username')
#         user = User.objects.get(username=username)
#     else :
#         return redirect('/showLogin')
# 
#     name = request.POST['name']
#     value = request.POST['value']
# 
#     SoilType(name=name,value=value).save();
#     
#     return redirect('/getSystemStatus')
# 
# def doAddIrrigationTemplate(request):
#     
#     name = request.POST['name']
#     series = request.POST['series']
#     
#     js = json.loads(series)
#     
#     template = IrrigationTemplate(name=name)
#     template.save()
#     for point in js['data'] :    
#         day_number=int(point['x'])
#         kc_value=float(point['y'])
#         KcValue(template=template,
#                 day_number=day_number,
#                 kc_value=kc_value).save()
#                                                            
#     return redirect('/getSystemStatus')
# 
# def showDeleteIrrigationTemplate(request):
#     
#     irrigationTemplates = IrrigationTemplate.objects.all()
#     
#     return render(request, 'IrrigationApp/pages/deleteIrrigationTemplate.html', { 'irrigationTemplates':irrigationTemplates })
# 
# def doDeleteIrrigationTemplate(request):
#     id = request.POST['irrigationTemplate']
#     
#     irrigationTemplate = IrrigationTemplate.objects.get(id=id)
#     kc_values = KcValue.objects.filter(template=irrigationTemplate)
#     for kc_value in kc_values :
#         template = ZoneTemplateValue.objects.get(kc_value=kc_value)
#         zone = template.zone
#         zone.irrigation_template=None
#         zone.save(update_fields=['irrigation_template'])
#     
#     KcValue.objects.filter(template=irrigationTemplate).delete()
#     irrigationTemplate.delete()
#     
#     return redirect('/getSystemStatus')
# 
# def showZoneTemplate(request):
#     zone_id = request.POST['zone_id']
#     zone = Zone.objects.get(id=zone_id)
#     
#     template_values = ZoneTemplateValue.objects.all()
#     
#     return render(request, 'IrrigationApp/pages/templateStatus.html', { 'template_values':template_values, 'zone':zone })
# 
# def showAddIrrigationTemplate(request):
#     return render(request, 'IrrigationApp/pages/addIrrigationTemplate.html', { })
#===============================================================================