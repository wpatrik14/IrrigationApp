from __future__ import absolute_import
from celery import Celery
import codecs
from datetime import datetime, timedelta
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from IrrigationApp.models import Pump, IrrigationTemplate, ZoneTemplateValue, KcValue, WeatherHistory, WeatherForecast, Sensor, Switch, Zone, SimpleSchedule, RepeatableSchedule, IrrigationHistory, IrrigationSettings, TaskQueue, SoilType
from django.http import HttpResponse
import json
import time
from urllib.request import urlopen
from celery import task
import subprocess

#app = Celery('tasks', backend="amqp", broker='amqp://guest@localhost:5672//', include=['celery.task.http'])
#app = Celery('tasks', include=['celery.task.http'])

celery = Celery('tasks', backend="amqp", broker='amqp://guest@localhost:5672//', include=['celery.task.http']) #!
celery.conf.update(CELERY_ACCEPT_CONTENT = ['json'])

def get_weather_data_from_server():
    res = urlopen('http://api.worldweatheronline.com/free/v1/weather.ashx?q=God&format=json&num_of_days=5&key=bffc71ad3fa08458dbf6fc77a0383cd421d61052')
    reader = codecs.getreader("utf-8")
    js = json.load(reader(res))
    
    humidity=js['data']['current_condition'][0]['humidity'];
    precipMM=js['data']['current_condition'][0]['precipMM'];
    cloudcover=js['data']['current_condition'][0]['cloudcover'];
    pressure=js['data']['current_condition'][0]['pressure'];
    temp_C=js['data']['current_condition'][0]['temp_C'];
    visibility=js['data']['current_condition'][0]['visibility'];
    windspeedKmph=js['data']['current_condition'][0]['windspeedKmph'];
    winddirDegree=js['data']['current_condition'][0]['winddirDegree'];
    place=js['data']['request'][0]['query'];
    icon=js['data']['current_condition'][0]['weatherIconUrl'][0]['value'];
    #current_weather='Observation time: {0}\nHumidity: {1}\nPrecipMM: {2}\nCloudcover: {3}\nPressure: {4}\nTemp (C): {5}\nVisibility: {6}\nWindspeed (Kmph): {7}\nWind direcion: {8}'.format(observation_time,humidity,precipMM,cloudcover,pressure,tempC,visibility,windspeedKmph,winddirDegree)
    
    mWeatherHistory = WeatherHistory(
        humidity=humidity,
        precipMM=precipMM,
        cloudcover=cloudcover,
        pressure=pressure,
        temp_C=temp_C,
        visibility=visibility,
        windspeedKmph=windspeedKmph,
        winddirDegree=winddirDegree,
        place=place,
        icon=icon)
    mWeatherHistory.save()
    
    date_0=js['data']['weather'][0]['date']
    precipMM_0=js['data']['weather'][0]['precipMM']
    tempMaxC_0=js['data']['weather'][0]['tempMaxC']
    tempMinC_0=js['data']['weather'][0]['tempMinC']
    icon_0=js['data']['weather'][0]['weatherIconUrl'][0]['value'];
    
    date_1=js['data']['weather'][1]['date']
    precipMM_1=js['data']['weather'][1]['precipMM']
    tempMaxC_1=js['data']['weather'][1]['tempMaxC']
    tempMinC_1=js['data']['weather'][1]['tempMinC']
    icon_1=js['data']['weather'][1]['weatherIconUrl'][0]['value'];
    
    date_2=js['data']['weather'][2]['date']
    precipMM_2=js['data']['weather'][2]['precipMM']
    tempMaxC_2=js['data']['weather'][2]['tempMaxC']
    tempMinC_2=js['data']['weather'][2]['tempMinC']
    icon_2=js['data']['weather'][2]['weatherIconUrl'][0]['value'];
    
    date_3=js['data']['weather'][3]['date']
    precipMM_3=js['data']['weather'][3]['precipMM']
    tempMaxC_3=js['data']['weather'][3]['tempMaxC']
    tempMinC_3=js['data']['weather'][3]['tempMinC']
    icon_3=js['data']['weather'][3]['weatherIconUrl'][0]['value'];
    
    date_4=js['data']['weather'][4]['date']
    precipMM_4=js['data']['weather'][4]['precipMM']
    tempMaxC_4=js['data']['weather'][4]['tempMaxC']
    tempMinC_4=js['data']['weather'][4]['tempMinC']
    icon_4=js['data']['weather'][4]['weatherIconUrl'][0]['value'];
        
    mWeatherForecast_0 = WeatherForecast(
        day=0,
        forecast_date=date_0,
        precipMM=precipMM_0,
        tempMax_C=tempMaxC_0,
        tempMin_C=tempMinC_0,
        icon=icon_0)
    mWeatherForecast_0.save()
    
    mWeatherForecast_1 = WeatherForecast(
        day=1,
        forecast_date=date_1,
        precipMM=precipMM_1,
        tempMax_C=tempMaxC_1,
        tempMin_C=tempMinC_1,
        icon=icon_1)
    mWeatherForecast_1.save()
    
    mWeatherForecast_2 = WeatherForecast(
        day=2,
        forecast_date=date_2,
        precipMM=precipMM_2,
        tempMax_C=tempMaxC_2,
        tempMin_C=tempMinC_2,
        icon=icon_2)
    mWeatherForecast_2.save()
    
    mWeatherForecast_3 = WeatherForecast(
        day=3,
        forecast_date=date_3,
        precipMM=precipMM_3,
        tempMax_C=tempMaxC_3,
        tempMin_C=tempMinC_3,
        icon=icon_3)
    mWeatherForecast_3.save()
    
    mWeatherForecast_4 = WeatherForecast(
        day=4,
        forecast_date=date_4,
        precipMM=precipMM_4,
        tempMax_C=tempMaxC_4,
        tempMin_C=tempMinC_4,
        icon=icon_4)
    mWeatherForecast_4.save()
    
    return

#@app.task
@task()
def get_weather_datas():
    
    get_weather_data_from_server()
    
    return '\n\nGETTING WEATHER DATAS........... DONE'

def setIrrigation(mZone, status):
        
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
    mSwitch = Switch.objects.get(pinNumber=mZone.switch.pinNumber)
    mSwitch.status = status
    mSwitch.save(update_fields=['status'])
    mZone.switch=mSwitch
    mZone.save(update_fields=['switch','up_time','irrigation_history']) 
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(mSwitch.pinNumber), str(mSwitch.status)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    switches = Switch.objects.all()
    running_zones=0;
    pump_status = 0
    
    pump=Pump.objects.get(id=0)
    
    for switch in switches :
        if switch.pinNumber != pump.switch.pinNumber :
            if switch.status == 1 :
                running_zones=running_zones+1
                pump_status = 1
        
    if pump_status == 1:
        pump_switch=pump.switch
        pump_switch.status=1
        pump_switch.save()
    else :
        pump_switch=pump.switch
        pump_switch.status=0
        pump_switch.save()
    
    pump.save(update_fields=['switch'])
    settings.running_zones=running_zones
    settings.save(update_fields=['running_zones'])
    
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(pump.switch.pinNumber), str(pump_status)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return

def addTaskToQueue(mZone):
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
    tasks = TaskQueue.objects.all().order_by('seq_number')
    TaskQueue(zone_id=mZone,
                          seq_number=len(tasks)+1).save()
    if len(tasks) < settings.runnable_zones_number :
        switchIrrigation(mZone,1)
    return

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
    return
    
def switchIrrigation(mZone, status):
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
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
                setIrrigation(mZone, 1)
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
                setIrrigation(mZone, 0)
        else :
            return 'Waiting for pump'

def changeZone(zone):    
    mZone = Zone.objects.get(id=zone.id)
    mZone.up_time=up_time
    mZone.save(update_fields=['up_time'])
    return

def changeSchedule(schedule, status):
    schedule.status=status
    schedule.save(update_fields=['status'])
    return


def forecastIrrigation():
    weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:1]
    if not weatherForecast.exists() :
        get_weather_data_from_server()
    
    weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:1]
    
    for zone in zones :
        if zone.type == "Automatic" :
            if zone.sensor.value<zone.moisture_minLimit :
                if zone.forecast_enabled :
                    if weatherForecast[0].precipMM < 0.5 :
                        #turn on irrigation if the precipitation of tomorrow will be less then 0.5 mm
                        addTaskToQueue(zone)
                    else :
                        deleteTaskFromQueue(zone)
                else :
                   #turn on irrigation anyway
                    addTaskToQueue(zone) 
                
            elif zone.sensor.value>zone.moisture_maxLimit:
                #turn off irrigation
                deleteTaskFromQueue(zone)
                zone.up_time=0
                zone.save(update_fields=['up_time'])
                
            if zone.switch.status == 1 :
                if zone.duration_today+2>zone.duration_maxLimit :
                    #turn off irrigation
                    deleteTaskFromQueue(zone)
                    zone.up_time=0
                    zone.save(update_fields=['up_time'])
                else :
                    settings = IrrigationSettings.objects.get(id=0)
                    zone.up_time=zone.up_time+1
                    zone.duration_today=zone.duration_today+1
                    zone.water_quantity=zone.water_quantity+5.5/float(zone.size_m2)/settings.running_zones
                    zone.save(update_fields=['up_time','duration_today','water_quantity'])
                    
        else :
            if zone.duration_today+1>zone.duration_maxLimit :
                #turn off irrigation
                deleteTaskFromQueue(zone)
                zone.up_time=0
                zone.save(update_fields=['up_time'])
            
            if zone.switch.status == 1 :
                settings = IrrigationSettings.objects.get(id=0)
                zone.up_time=zone.up_time+1
                zone.duration_today=zone.duration_today+1
                zone.water_quantity=zone.water_quantity+5.5/float(zone.size_m2)/settings.running_zones
                zone.save(update_fields=['up_time','duration_today','water_quantity'])
                
            else :
                zone.up_time=0
                zone.save(update_fields=['up_time'])


#@app.task
@task()
def automation_control():
    reader = codecs.getreader("utf-8")
    result=""
    
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withresponse', '0', '0', '1', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    with open('/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/output.txt','r') as file:
        result=str(file.read())
        js = json.loads(result)
        Switch(pinNumber=int(js['Pin']),status=int(js['Stat'])).save()
    
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withresponse', '0', '0', '2', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    with open('/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/output.txt','r') as file:
        result=str(file.read())
        js = json.loads(result)
        Switch(pinNumber=int(js['Pin']),status=int(js['Stat'])).save()
    
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withresponse', '0', '1', '0', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    with open('/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/output.txt','r') as file:
        result=str(file.read())
        js = json.loads(result)
        Sensor(node=int(js['Node']),value=int(js['Stat'])).save()
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
    settings.flow_meter=4
    settings.save(update_fields=['flow_meter'])
    
    zones = Zone.objects.all()
    
    
    
    tasks = TaskQueue.objects.all()
    if len(tasks) > settings.runnable_zones_number-1 :
        for i in range(settings.runnable_zones_number) :
            task = TaskQueue.objects.get(seq_number=i+1)
            zone=task.zone_id
            if zone.switch.status == 0 :
                switchIrrigation(zone, 1)
    
    
    
    settings = IrrigationSettings.objects.get(id=0)
    settings.water = settings.water + 5.5
    settings.total_cost=settings.total_cost+settings.cost_perLiter*5.5
    settings.save(update_fields=['water','total_cost'])
    
    pump = Pump.objects.get(id=0)
    if pump.switch.status == 1:
        pump.up_time = pump.up_time + 1
    else :
        pump.down_time = pump.down_time + 1
    
    pump.save(update_fields=['up_time','down_time'])
            
    return '\n\nAUTOMATION CONTROL........... DONE'

#@app.task
@task()
def scheduler():
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return "Please set up settings first"
    
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    dayNumber = datetime.now().strftime("%w")
    days = ['sunday','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    
    ### STARTING / END SCHEDULES
    for simpleSchedule in simpleSchedules :
        if str(simpleSchedule.date) == str(date) :
            if str(time) in str(simpleSchedule.time) :
                switchIrrigation(simpleSchedule.zone, 1)
                changeSchedule(simpleSchedule,'running')
            
        if simpleSchedule.status == 'running' :
            if int(simpleSchedule.zone.up_time) == int(simpleSchedule.duration) or int(simpleSchedule.zone.up_time) == int(simpleSchedule.zone.duration_maxLimit) or simpleSchedule.zone.switch.status == 'off':
                simpleSchedule.delete()
                switchIrrigation(simpleSchedule.zone, 0)
                
    for repeatableSchedule in repeatableSchedules :
        if repeatableSchedule.day == days[int(dayNumber)] :
            if str(time) in str(repeatableSchedule.time) :
                switchIrrigation(repeatableSchedule.zone, 1)
                changeSchedule(repeatableSchedule,'running')
            
        if repeatableSchedule.status == 'running' :
            if int(repeatableSchedule.zone.up_time) == int(repeatableSchedule.duration) or int(repeatableSchedule.zone.up_time) == int(repeatableSchedule.zone.duration_maxLimit) or repeatableSchedule.zone.switch.status == 'off':
                switchIrrigation(repeatableSchedule.zone, 0)
                changeSchedule(repeatableSchedule,'stopped')
                
                           
    return '\n\nSCHEDULER........... DONE'


#@app.task
@task()
def follow_irrigation_template():
    
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return "Please set up settings first"
    
    irrigationTemplates = IrrigationTemplate.objects.all()
    zones = Zone.objects.all()
    
    for zone in zones :
        zone.duration_today=0
        zone.water_quantity=0
        zone.save(update_fields=['duration_today','water_quantity'])
        if zone.irrigation_template is not None :
            try:
                templateValues = ZoneTemplateValue.objects.filter(zone=zone)
                required_irrigation=False
                for templateValue in templateValues :
                    if templateValue.kc_value.day_number == zone.template_day_counter :
                        if zone.type == 'Automatic' :
                            if templateValue.irrigation_required == True :
                                required_irrigation=True
                if required_irrigation == True :
                    irrigation_date = datetime.now() + timedelta(hours=1)
                    date = irrigation_date.strftime("%Y-%m-%d")
                    time = irrigation_date.strftime("%H:%M")
                    duration = templateValue.runtime
                    zones = Zone.objects.all()
                    schedule=SimpleSchedule(date=date,
                                   time=time,
                                   duration=duration,
                                   zone=zone)
                    schedule.save()                
                zone.template_day_counter=zone.template_day_counter+1
                zone.save(update_fields=['template_day_counter'])
                                
            except Exception as e :
                switchIrrigation(zone, 0)
                zone.type='Manual'
                zone.template=None
                zone.template_day_counter=0
                zone.save(update_fields=['type','template','template_day_counter'])
    
    
    return '\n\nFOLLOWING IRRIGATION TEMPLATE...........DONE'
