from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class WeatherHistory(models.Model):
    temp_C = models.IntegerField(max_length=3)
    humidity = models.IntegerField(max_length=3)
    cloudcover = models.IntegerField(max_length=5)
    pressure = models.IntegerField(max_length=5)
    visibility = models.IntegerField(max_length=5)
    precipMM=models.FloatField(max_length=4)
    icon=models.TextField()
    observation_time=models.DateTimeField(default=datetime.now, blank=True)
    windspeedKmph = models.IntegerField(max_length=5)
    winddirDegree = models.IntegerField(max_length=5)
    place = models.CharField(max_length=30)
    def __unicode__(self):
        return self.temp_C + ' ' + self.precip_MM
        
class WeatherForecast(models.Model):
    day = models.IntegerField(max_length=1, primary_key=True)
    tempMax_C = models.IntegerField(max_length=3)
    tempMin_C = models.IntegerField(max_length=3)
    precipMM=models.FloatField(max_length=4)
    forecast_date=models.DateField(primary_key=True)
    update=models.DateTimeField(default=datetime.now, blank=True)
    icon=models.TextField()
    def __unicode__(self):
        return self.tempMax_C + ' ' + self.tempMin_C
    
class Segment(models.Model):
    sensor = models.ForeignKey('Sensor')
    switch = models.ForeignKey('Switch')
    name=models.CharField(max_length=20)
    up_time=models.IntegerField(max_length=3, default=0)
    moisture_minLimit=models.IntegerField(max_length=5)
    moisture_maxLimit=models.IntegerField(max_length=5)
    duration_maxLimit=models.IntegerField(max_length=3)
    forecast_enabled=models.BooleanField(default=False)
    type=models.CharField(max_length=10)
    irrigation_history=models.ForeignKey('IrrigationHistory', null = True)
    template=models.ForeignKey('IrrigationTemplate', null = True)
    def __unicode__(self):
        return self.sensor + ' ' + self.switch  

class Sensor(models.Model):
    pinNumber = models.CharField(max_length=3, primary_key=True)
    status = models.IntegerField(max_length=3)
    def __unicode__(self):
        return self.pinNumber + ' ' + self.status 
    
class Switch(models.Model):
    pinNumber = models.CharField(max_length=3, primary_key=True)
    status = models.CharField(max_length=3)
    def __unicode__(self):
        return self.pinNumber + ' ' + self.status 
    
class SimpleSchedule(models.Model):
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(max_length=3)
    segment = models.ForeignKey('Segment')
    status = models.CharField(max_length=10, default='stopped')
    def __unicode__(self):
        return self.enabled + ' ' + self.segment 
    
class RepeatableSchedule(models.Model):
    name = models.CharField(max_length=20)
    day = models.CharField(max_length=10)
    time = models.TimeField()
    duration = models.IntegerField(max_length=3)
    segment = models.ForeignKey('Segment')
    status = models.CharField(max_length=10, default='stopped')  
    def __unicode__(self):
        return self.enabled + ' ' + self.segment  
    
class IrrigationHistory(models.Model):
    segment_id = models.ForeignKey('Segment')
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    end_date = models.DateTimeField(default=datetime.now, blank=True)
    duration = models.IntegerField(max_length=3, default=0)
    moisture_startValue = models.IntegerField(max_length=3)
    moisture_endValue = models.IntegerField(max_length=3,default=0)
    status = models.CharField(max_length=10, default='running')
    def __unicode__(self):
        return self.start_date + ' ' + self.end_date
    
class IrrigationTemplateValue(models.Model):
    template = models.ForeignKey('IrrigationTemplate')
    day_number = models.IntegerField(max_length=3)
    value = models.IntegerField(max_length=4)
    def __unicode__(self):
        return self.day_number + ' ' + self.values
    
class IrrigationTemplate(models.Model):
    segment_id = models.ForeignKey('Segment')
    day_counter = models.IntegerField(max_length=3, default=0)
    name = models.CharField(max_length=15)
    def __unicode__(self):
        return self.template + ' ' + self.segment

class Arduino(models.Model):
    id = models.IntegerField(max_length=1, primary_key=True)
    IP = models.CharField(max_length=17)
    PORT = models.CharField(max_length=5)
    def __unicode__(self):
        return self.IP
   
class IrrigationSettings(models.Model):
    id = models.IntegerField(max_length=1, primary_key=True)
    pump = models.ForeignKey('Switch')
    def __unicode__(self):
        return self.pump
