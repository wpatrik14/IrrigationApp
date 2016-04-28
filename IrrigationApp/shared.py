
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
#import paho.mqtt.publish as publish

def setIrrigation(mZone, status):
    settings = IrrigationSettings.objects.all()
    if settings.exists() :
        settings = IrrigationSettings.objects.get(id=0)
    else:
        return redirect('/showAddSettings')
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(mZone.switch.pinNumber), str(status)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    mSwitch = Switch.objects.get(pinNumber=mZone.switch.pinNumber)
    mSwitch.status = status
    mSwitch.save(update_fields=['status'])
    mZone.switch=mSwitch
    mZone.save(update_fields=['switch','up_time','irrigation_history'])        
    #publish.single("irrigationapp/switch", "{\"Node\":\"0\",\"Command\":\"2\",\"Pin\":\""+str(mSwitch.pinNumber)+"\",\"Stat\":\""+str(mSwitch.status)+"\"", hostname="iot.eclipse.org")
    
#     switches = Switch.objects.all()
#     running_zones=0;
#     pump_status = False
#     pump=Pump.objects.get(id=0)
#     
#     for switch in switches :
#         if switch.pinNumber != pump.switch.pinNumber :
#             if switch.status == 1 :
#                 running_zones=running_zones+1
#                 pump_status = True
#         
#     if pump_status :
#         pump.switch.status = 1
#     else :
#         pump.switch.status = 0
#     pump.save()
#     settings.running_zones=running_zones
#     settings.save(update_fields=['running_zones'])
#     subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', '1', '0', str(pump.switch.pinNumber), str(pump.switch.status)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     #publish.single("irrigationapp/switch", "{\"Node\":\"0\",\"Command\":\"2\",\"Pin\":\""+str(pump.switch.pinNumber)+"\",\"Stat\":\""+str(pump_status)+"\"", hostname="iot.eclipse.org")
    
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
        