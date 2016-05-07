from __future__ import absolute_import
from celery import Celery
import codecs
from datetime import datetime, timedelta
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from IrrigationApp.models import Pump, IrrigationTemplate, MoistureHistory, ZoneTemplateValue, KcValue, WeatherHistory, WeatherForecast, Sensor, Switch, Zone, SimpleSchedule, RepeatableSchedule, IrrigationHistory, IrrigationSettings, TaskQueue, SoilType
from django.http import HttpResponse
import json
import time
from urllib.request import urlopen
from celery import task
import subprocess
#import paho.mqtt.publish as publish
from IrrigationApp.shared import setIrrigation, switchIrrigation, addTaskToQueue, deleteTaskFromQueue

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

@task()
def get_weather_datas():
    
    get_weather_data_from_server()
    
    return '\n\nGETTING WEATHER DATAS........... DONE'


def changeZone(zone):    
    mZone = Zone.objects.get(id=zone.id)
    mZone.up_time=up_time
    mZone.save(update_fields=['up_time'])
    return

def changeSchedule(schedule, status):
    schedule.status=status
    schedule.save(update_fields=['status'])
    return
        
@task()
def automation_control():
        
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'
    
    zones = Zone.objects.all()
    before = (datetime.now() - timedelta(minutes=2)).strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d")
    for zone in zones :
        if before != now :
            zone.duration_today=0
        
        if zone.switch.status == 1 :
            zone.up_time=zone.up_time+1
            zone.duration_today=zone.duration_today+1
        
        if zone.up_time == -1 :
            zone.up_time=0
        zone.save(update_fields=['up_time','duration_today'])
        
        if zone.duration_today>=zone.duration_maxLimit and zone.switch.status == 1 :
            switchIrrigation(zone,"0")
        
        if zone.forecast_enabled :
            irrigationStatus=str(zone.switch.status)
            weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:4]
            if not weatherForecast.exists() :
                get_weather_data_from_server()
                weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:4]
            precipMM = weatherForecast[0].precipMM + weatherForecast[1].precipMM + weatherForecast[2].precipMM
            if precipMM >= zone.moisture_minLimit and zone.switch.status == 1 :
                switchIrrigation(zone,"0")
    
    time.sleep(3)
    
    date = datetime.now().strftime("%Y-%m-%d")
    cur_time = datetime.now().strftime("%H:%M")
    dayNumber = datetime.now().strftime("%w")
    days = ['sunday','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    simpleSchedules = SimpleSchedule.objects.all()
    repeatableSchedules = RepeatableSchedule.objects.all()
    
    ### STARTING / END SCHEDULES
    for simpleSchedule in simpleSchedules :
        if str(simpleSchedule.date) == str(date) :
            if str(cur_time) in str(simpleSchedule.time) :
                switchIrrigation(simpleSchedule.zone, "1")
                changeSchedule(simpleSchedule,'running')
            
        if simpleSchedule.status == 'running' :
            if int(simpleSchedule.zone.up_time) == int(simpleSchedule.duration) or int(simpleSchedule.zone.up_time) == int(simpleSchedule.zone.duration_maxLimit) or simpleSchedule.zone.switch.status == 'off':
                simpleSchedule.delete()
                switchIrrigation(simpleSchedule.zone, "0")
                
    for repeatableSchedule in repeatableSchedules :
        if repeatableSchedule.day == days[int(dayNumber)] :
            if str(cur_time) in str(repeatableSchedule.time) :
                switchIrrigation(repeatableSchedule.zone, "1")
                changeSchedule(repeatableSchedule,'running')
            
        if repeatableSchedule.status == 'running' :
            if int(repeatableSchedule.zone.up_time) == int(repeatableSchedule.duration) or int(repeatableSchedule.zone.up_time) == int(repeatableSchedule.zone.duration_maxLimit) or repeatableSchedule.zone.switch.status == 'off':
                switchIrrigation(repeatableSchedule.zone, "0")
                changeSchedule(repeatableSchedule,'stopped')
            
    return '\n\nAUTOMATION CONTROL........... DONE'

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
                runtime = 0
                for templateValue in templateValues :
                    if templateValue.kc_value.day_number == zone.template_day_counter :
                        if zone.type == 'Automatic' :
                            if templateValue.irrigation_required == True :
                                required_irrigation=True
                                runtime = templateValue.runtime
                if required_irrigation == True :
                    irrigation_date = datetime.now() + timedelta(hours=1)
                    date = irrigation_date.strftime("%Y-%m-%d")
                    time = irrigation_date.strftime("%H:%M")
                    zones = Zone.objects.all()
                    schedule=SimpleSchedule(date=date,
                                   time=time,
                                   duration=runtime,
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


@task()
def getSensorData():
    zones=Zone.objects.all()
    for zone in zones :
        subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withresponse', '0', str(zone.sensor.node), '0', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        with open('/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/output.txt','r') as file:
            result=str(file.read())
            js = json.loads(result)
            sensor=Sensor(node=js['Node'],value=int(js['Stat']))
            sensor.save()
            MoistureHistory(zone_id=zone,value=sensor.value,date=datetime.now()).save()
        #publish.single("irrigationapp/sensor", "{\"Node\":\""+js['Node']+"\",\"Value\":\""+js['Stat']+"\"", hostname="iot.eclipse.org")
            
    return '\n\nGET SENSOR DATA...........DONE'