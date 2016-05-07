
from IrrigationApp.models import MoistureHistory, Pump, IrrigationTemplate, ZoneTemplateValue, KcValue, IrrigationSettings, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Zone, Switch, Sensor, IrrigationHistory, SoilType, TaskQueue
import subprocess
from django.utils import timezone
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time
import codecs
import json
import logging
import time
import math
import random
#import paho.mqtt.publish as publish

def setIrrigation(mZone, status):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    seq=random.randint(1, 10)
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', str(seq), str(mZone.switch.pinNumber), str(status)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(2)
    with open('/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/output.txt','r') as file:
        result=str(file.read())
        js = json.loads(result)
        r_seq=js['Seq']
        if r_seq==str(seq) :
            pin=js['Pin']
            stat=js['Stat']
            mSwitch = Switch.objects.get(pinNumber=pin)
            mSwitch.status = stat
            mSwitch.save(update_fields=['status'])
            mZone.switch=mSwitch
            mZone.save(update_fields=['switch','up_time','irrigation_history','moisture_maxLimit'])
    
    return
    
def addTaskToQueue(mZone):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return 'Settings not found'

    if getRunningZonesNumber() < settings.runnable_zones_number :
        switchIrrigation(mZone,1)
    else :
        tasks = TaskQueue.objects.all()
        TaskQueue(zone_id=mZone,seq_number=len(tasks)+1).save()
        #publish.single("irrigationapp/task", "Added", hostname="iot.eclipse.org")

def getRunningZonesNumber():
    switches = Switch.objects.all()
    pump=Pump.objects.get(id=0)
    running_zones=0;
    
    for switch in switches :
        if switch.pinNumber != pump.switch.pinNumber :
            if switch.status == 1 :
                running_zones=running_zones+1
    return running_zones;
        
def deleteTaskFromQueue(mZone):
    if mZone.switch.status == 1:
        tasks = TaskQueue.objects.all().order_by('seq_number')
        if len(tasks) > 1 :
            deleted_task=TaskQueue.objects.get(zone_id=mZone)
            seq_number=deleted_task.seq_number
            deleted_task.delete()
            #publish.single("irrigationapp/task", "Deleted", hostname="iot.eclipse.org")
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
    
    if status == "1" and mZone.switch.status == 0 and mZone.duration_today<mZone.duration_maxLimit and mZone.up_time == 0 :
        if mZone.irrigation_enabled or not mZone.forecast_enabled :
            if mZone.irrigation_history is None :
                mIrrigationHistory = IrrigationHistory(zone_id=mZone,
                                                                   moisture_startValue=mZone.sensor.value
                                                                   )
                mIrrigationHistory.save()
                mZone.irrigation_history=mIrrigationHistory
            setIrrigation(mZone, 1)
                    
    else :         
        if mZone.switch.status == 1 and mZone.irrigation_history is not None and mZone.up_time > 0 :
            mHistory=IrrigationHistory.objects.get(id=mZone.irrigation_history.id)
            mHistory.end_date=datetime.now()
            mHistory.duration=mZone.up_time+1
            mHistory.moisture_endValue=mZone.sensor.value
            mHistory.status='done'
            mHistory.save(update_fields=['end_date','duration','moisture_endValue','status'])
            mZone.up_time = -1
            mZone.irrigation_history=None
            if mZone.current_pipe == 6 :
                mZone.current_pipe = 1
            else :
                mZone.current_pipe = mZone.current_pipe + 1
            setIrrigation(mZone, 0)

    return