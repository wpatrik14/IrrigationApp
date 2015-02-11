from __future__ import absolute_import
from celery import Celery
import codecs
from datetime import datetime
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from IrrigationApp.models import WeatherHistory, WeatherForecast, Sensor, Switch, Segment, SimpleSchedule, RepeatableSchedule, IrrigationHistory, IrrigationSettings, Arduino
from django.http import HttpResponse
import json
import time
from urllib.request import urlopen

app = Celery('tasks', backend="amqp", broker='amqp://guest@localhost:5672//', include=['celery.task.http'])

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
        forecast_date=date_0,
        precipMM=precipMM_0,
        tempMax_C=tempMaxC_0,
        tempMin_C=tempMinC_0,
        icon=icon_0)
    mWeatherForecast_0.save()
    
    mWeatherForecast_1 = WeatherForecast(
        forecast_date=date_1,
        precipMM=precipMM_1,
        tempMax_C=tempMaxC_1,
        tempMin_C=tempMinC_1,
        icon=icon_1)
    mWeatherForecast_1.save()
    
    mWeatherForecast_2 = WeatherForecast(
        forecast_date=date_2,
        precipMM=precipMM_2,
        tempMax_C=tempMaxC_2,
        tempMin_C=tempMinC_2,
        icon=icon_2)
    mWeatherForecast_2.save()
    
    mWeatherForecast_3 = WeatherForecast(
        forecast_date=date_3,
        precipMM=precipMM_3,
        tempMax_C=tempMaxC_3,
        tempMin_C=tempMinC_3,
        icon=icon_3)
    mWeatherForecast_3.save()
    
    mWeatherForecast_4 = WeatherForecast(
        forecast_date=date_4,
        precipMM=precipMM_4,
        tempMax_C=tempMaxC_4,
        tempMin_C=tempMinC_4,
        icon=icon_4)
    mWeatherForecast_4.save()
    
    return

@app.task
def get_weather_datas():
    
    get_weather_data_from_server()
    
    return '\n\nGETTING WEATHER DATAS........... DONE'

def switchIrrigation(mSegment, status, settings, arduino):
    
    if status == 'on' :
        mSegment.up_time = mSegment.up_time
        if mSegment.irrigation_history is None :
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
        mSegment.irrigation_history=None
    
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
    pump.status = pump_status
    pump.save(update_fields=['status'])
    settings.pump=pump
    settings.save(update_fields=['pump'])
    if pump.status :
        status = "on"
    else :
        status = "off"
    urlopen("http://"+arduino.IP+":"+arduino.PORT+"/?pinNumber="+pump.pinNumber+"&status="+status)
    
    return

def changeSegment(segment, up_time):    
    mSegment = Segment.objects.get(id=segment.id)
    mSegment.up_time=up_time
    mSegment.save(update_fields=['up_time'])
    return

def changeSchedule(schedule, status):
    schedule.status=status
    schedule.save(update_fields=['status'])
    return

@app.task
def automation_control():
    
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
    
    segments = Segment.objects.all()
    
    weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:1]
    if not weatherForecast.exists() :
        get_weather_data_from_server()
    
    weatherForecast = WeatherForecast.objects.all().order_by('forecast_date')[:1]
    
    for segment in segments :
        if segment.type == "Automatic" :
            if segment.sensor.status>segment.moisture_minLimit :
                if segment.forecast_enabled :
                    if weatherForecast[0].precipMM < 0.5 :
                        #turn on irrigation if the precipitation of tomorrow will be less then 0.5 mm
                        switchIrrigation(segment, 'on', settings, arduino)
                    else :
                        switchIrrigation(segment, 'off', settings, arduino)
                else :
                   #turn on irrigation anyway
                    switchIrrigation(segment, 'on', settings, arduino) 
                
            elif segment.sensor.status<segment.moisture_maxLimit:
                #turn off irrigation
                switchIrrigation(segment, 'off', settings, arduino)
                changeSegment(segment, 0)
                
            if segment.switch.status == "on" :
                if segment.up_time+2>segment.duration_maxLimit :
                    #turn off irrigation
                    switchIrrigation(segment, 'off', settings, arduino)
                    changeSegment(segment, 0)
                else :
                    changeSegment(segment, segment.up_time+1)
        else :
            if segment.up_time+2>segment.duration_maxLimit :
                #turn off irrigation
                switchIrrigation(segment, 'off', settings, arduino)
                changeSegment(segment, 0)
            
            if segment.switch.status == "on" :
                changeSegment(segment, segment.up_time+1)
            else :
                changeSegment(segment, 0)
            
    return '\n\nAUTOMATION CONTROL........... DONE'

@app.task
def scheduler():
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
                switchIrrigation(simpleSchedule.segment, 'on', settings, arduino)
                changeSchedule(simpleSchedule,'running')
            
        if simpleSchedule.status == 'running' :
            if int(simpleSchedule.segment.up_time) == int(simpleSchedule.duration) or int(simpleSchedule.segment.up_time) == int(simpleSchedule.segment.duration_maxLimit) or simpleSchedule.segment.switch.status == 'off':
                simpleSchedule.delete()
                switchIrrigation(simpleSchedule.segment, 'off', settings, arduino)
                
    for repeatableSchedule in repeatableSchedules :
        if repeatableSchedule.day == days[int(dayNumber)] :
            if str(time) in str(repeatableSchedule.time) :
                switchIrrigation(repeatableSchedule.segment, 'on', settings, arduino)
                changeSchedule(repeatableSchedule,'running')
            
        if repeatableSchedule.status == 'running' :
            if int(repeatableSchedule.segment.up_time) == int(repeatableSchedule.duration) or int(repeatableSchedule.segment.up_time) == int(repeatableSchedule.segment.duration_maxLimit) or repeatableSchedule.segment.switch.status == 'off':
                switchIrrigation(repeatableSchedule.segment, 'off', settings, arduino)
                changeSchedule(repeatableSchedule,'stopped')
                
                           
    return '\n\nSCHEDULER........... DONE'