from __future__ import absolute_import
from celery import Celery
from urllib.request import urlopen
import codecs
from datetime import datetime
from IrrigationApp.models import WeatherHistory, Sensor, Switch, Segment
from django.http import HttpResponse
import json
import requests
import time

app = Celery('tasks', backend="amqp", broker='amqp://guest@localhost:5672//', include=['celery.task.http'])

@app.task
def get_weather_datas():
    
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
    
    return '\n\n\nGETTING WEATHER DATAS........... DONE'

@app.task
def automation_control():
    
    res = urlopen('http://192.168.0.105')
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
    for segment in segments :
        if segment.type == "Automatic" :
            if segment.sensor.status>segment.moisture_minLimit:
                #turn on irrigation
                r = requests.get("http://192.168.0.105:80/?pinNumber="+segment.switch.pinNumber+"&status=on")
                mSwitch = Switch(
                                pinNumber=segment.switch.pinNumber,
                                status="on")
                mSwitch.save()
            elif segment.sensor.status<segment.moisture_maxLimit:
                #turn off irrigation
                r = requests.get("http://192.168.0.105:80/?pinNumber="+segment.switch.pinNumber+"&status=off")
                mSwitch = Switch(
                            pinNumber=segment.switch.pinNumber,
                            status="off")
                mSwitch.save()
                mSegment = Segment(
                        id=segment.id,
                        name = segment.name,
                        sensor = segment.sensor,
                        switch = segment.switch,
                        up_time = 0,
                        moisture_minLimit = segment.moisture_minLimit,
                        moisture_maxLimit = segment.moisture_maxLimit,
                        duration_maxLimit = segment.duration_maxLimit,
                        forecast_enabled = segment.forecast_enabled,
                        type = segment.type
                                )
                mSegment.save()
                
                
            if segment.switch.status == "on" :
                if segment.up_time+2>segment.duration_maxLimit :
                    #turn off irrigation
                    r = requests.get("http://192.168.0.105:80/?pinNumber="+segment.switch.pinNumber+"&status=off")
                    mSwitch = Switch(
                            pinNumber=segment.switch.pinNumber,
                            status="off")
                    mSwitch.save()
                    mSegment = Segment(
                        id=segment.id,
                        name = segment.name,
                        sensor = segment.sensor,
                        switch = segment.switch,
                        up_time = 0,
                        moisture_minLimit = segment.moisture_minLimit,
                        moisture_maxLimit = segment.moisture_maxLimit,
                        duration_maxLimit = segment.duration_maxLimit,
                        forecast_enabled = segment.forecast_enabled,
                        type = segment.type
                                )
                    mSegment.save()
                else :
                    mSegment = Segment(
                            id=segment.id,
                            name = segment.name,
                            sensor = segment.sensor,
                            switch = segment.switch,
                            up_time = segment.up_time+1,
                            moisture_minLimit = segment.moisture_minLimit,
                            moisture_maxLimit = segment.moisture_maxLimit,
                            duration_maxLimit = segment.duration_maxLimit,
                            forecast_enabled = segment.forecast_enabled,
                            type = segment.type
                                    )
                    mSegment.save()
        else :
            if segment.switch.status == "on" :
                mSegment = Segment(
                        id=segment.id,
                        name = segment.name,
                        sensor = segment.sensor,
                        switch = segment.switch,
                        up_time = segment.up_time+1,
                        moisture_minLimit = segment.moisture_minLimit,
                        moisture_maxLimit = segment.moisture_maxLimit,
                        duration_maxLimit = segment.duration_maxLimit,
                        forecast_enabled = segment.forecast_enabled,
                        type = segment.type
                                )
                mSegment.save()
            else :
                mSegment = Segment(
                        id=segment.id,
                        name = segment.name,
                        sensor = segment.sensor,
                        switch = segment.switch,
                        up_time = 0,
                        moisture_minLimit = segment.moisture_minLimit,
                        moisture_maxLimit = segment.moisture_maxLimit,
                        duration_maxLimit = segment.duration_maxLimit,
                        forecast_enabled = segment.forecast_enabled,
                        type = segment.type
                                )
                mSegment.save()
            
    return '\n\n\n\n\n\nAUTOMATION CONTROL........... DONE'

@app.task
def scheduler():
    
    return '\n\n\n\n\n\nSCHEDULER........... DONE'