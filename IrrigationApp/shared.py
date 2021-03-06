
from IrrigationApp.models import MoistureHistory, SimpleSchedule, RepeatableSchedule, WeatherHistory, WeatherForecast, Zone, Switch, Sensor, IrrigationHistory
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
from django.core.mail import send_mail

def setIrrigation(mZone, status):
    seq=random.randint(0, 9)
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', str(seq), str(mZone.switch.pinNumber), str(status)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
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
            mZone.type="OK"
            if status == 1 :
                if mZone.irrigation_history is None :
                    mIrrigationHistory = IrrigationHistory(zone_id=mZone,
                                                                   moisture_startValue=mZone.sensor.value
                                                                   )
                    mIrrigationHistory.save()
                    mZone.irrigation_history=mIrrigationHistory
            else :
                if mZone.irrigation_history is not None :
                    mHistory=IrrigationHistory.objects.get(id=mZone.irrigation_history.id)
                    mHistory.end_date=datetime.now()
                    mHistory.duration=mZone.up_time
                    mHistory.moisture_endValue=mZone.sensor.value
                    mHistory.status='done'
                    mHistory.save(update_fields=['end_date','duration','moisture_endValue','status'])
                mZone.up_time = -1
                mZone.irrigation_history=None
                if mZone.current_pipe == 4 :
                    mZone.current_pipe = 1
                else :
                    mZone.current_pipe = mZone.current_pipe + 1
            
            mZone.save(update_fields=['switch','up_time','irrigation_history','current_pipe','type'])
            return True
        else :
            mZone.type="ERROR"
            send_mail('ERROR in Irrigation System', 'No connection between Raspberry and Arduino', 'godlocsolas@gmail.com',['godlocsolas@gmail.com'], fail_silently=False)
            return False
    
def switchIrrigation(mZone, status):   
    if status == "1" :
        if mZone.switch.status == 0 and mZone.up_time == 0 and mZone.irrigation_enabled :
            return setIrrigation(mZone, 1)      
    else :
        if mZone.switch.status == 1 and mZone.up_time > 0 :
            return setIrrigation(mZone, 0)

def checkZone(mZone):
    seq=random.randint(0, 9)
    subprocess.Popen(['sudo','/home/pi/rf24libs/stanleyseow/RF24/RPi/RF24/examples/radiomodule_withoutresponse', str(seq), str(mZone.switch.pinNumber), "2"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
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
            mZone.type="OK"
            mZone.save(update_fields=['type'])
            return True
        else :
            mZone.type="ERROR"
            mZone.save(update_fields=['type'])
            send_mail('ERROR in Irrigation System', 'No connection between Raspberry and Arduino', 'godlocsolas@gmail.com',['godlocsolas@gmail.com'], fail_silently=False)
            return False        

# def addTaskToQueue(mZone):
#     settings = IrrigationSettings.objects.all()
#     if settings.exists() :
#         settings = IrrigationSettings.objects.get(id=0)
#     else:
#         return 'Settings not found'
# 
#     if getRunningZonesNumber() < settings.runnable_zones_number :
#         switchIrrigation(mZone,1)
#     else :
#         tasks = TaskQueue.objects.all()
#         TaskQueue(zone_id=mZone,seq_number=len(tasks)+1).save()
#         #publish.single("irrigationapp/task", "Added", hostname="iot.eclipse.org")
# 
# def getRunningZonesNumber():
#     switches = Switch.objects.all()
#     pump=Pump.objects.get(id=0)
#     running_zones=0;
#     
#     for switch in switches :
#         if switch.pinNumber != pump.switch.pinNumber :
#             if switch.status == 1 :
#                 running_zones=running_zones+1
#     return running_zones;
#         
# def deleteTaskFromQueue(mZone):
#     if mZone.switch.status == 1:
#         tasks = TaskQueue.objects.all().order_by('seq_number')
#         if len(tasks) > 1 :
#             deleted_task=TaskQueue.objects.get(zone_id=mZone)
#             seq_number=deleted_task.seq_number
#             deleted_task.delete()
#             #publish.single("irrigationapp/task", "Deleted", hostname="iot.eclipse.org")
#             switchIrrigation(mZone, 0)
#             tasks = TaskQueue.objects.all().order_by('seq_number')
#             if tasks is not None:
#                 for task in tasks :
#                     if task.seq_number>seq_number:
#                         temp=TaskQueue.objects.get(zone_id=task.zone_id)
#                         temp.seq_number=temp.seq_number-1
#                         temp.save()
#         else :
#             switchIrrigation(mZone, 0)