from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
  
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    fullname = models.CharField(max_length=50)
    ip_address = models.IPAddressField()
    port = models.IntegerField(max_length=5)
    def __unicode__(self):
        return self.fullname + ' ' + self.ip_address

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
    tempMax_C = models.IntegerField(max_length=3)
    tempMin_C = models.IntegerField(max_length=3)
    precipMM=models.IntegerField(max_length=4)
    forecast_date=models.DateField()
    update=models.DateField()
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
    segment = models.ForeignKey('Segment')
    date = models.DateField()
    duration = models.IntegerField(max_length=8)
    moisture_startValue = models.IntegerField(max_length=3)
    moisture_endValue = models.IntegerField(max_length=3)
    def __unicode__(self):
        return self.segment + ' ' + self.date
    
class IrrigationTemplate(models.Model):
    name = models.CharField(max_length=20)
    values = models.TextField()
    def __unicode__(self):
        return self.name + ' ' + self.values
    
class IrrigationTemplateControl(models.Model):
    template = models.ForeignKey('IrrigationTemplate')
    segment = models.ForeignKey('Segment')
    day_counter = models.IntegerField(max_length=3)
    def __unicode__(self):
        return self.template + ' ' + self.segment
    
class IrrigationSettings(models.Model):
    user = models.ForeignKey('UserProfile')
    type = models.CharField(max_length=20)
    def __unicode__(self):
        return self.user + ' ' + self.type
