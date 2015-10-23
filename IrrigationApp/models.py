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
    forecast_date=models.DateField()
    update=models.DateTimeField(default=datetime.now, blank=True)
    icon=models.TextField()
    def __unicode__(self):
        return self.tempMax_C + ' ' + self.tempMin_C
    
class Zone(models.Model):
    sensor = models.ForeignKey('Sensor')
    switch = models.ForeignKey('Switch')
    name=models.CharField(max_length=20)
    up_time=models.IntegerField(max_length=3, default=0)
    moisture_minLimit=models.IntegerField(max_length=5)
    moisture_maxLimit=models.IntegerField(max_length=5)
    duration_maxLimit=models.IntegerField(max_length=3)
    duration_today=models.IntegerField(default=0)
    forecast_enabled=models.BooleanField(default=False)
    type=models.CharField(max_length=10)
    irrigation_history=models.ForeignKey('IrrigationHistory', null = True)
    template=models.ForeignKey('IrrigationTemplate', null = True)
    size_m2=models.IntegerField(default=0)
    root_length=models.IntegerField(default=20)
    moisture_deviation=models.IntegerField(max_length=3)
    efficiency=models.IntegerField(max_length=3)
    soil_type=models.ForeignKey('SoilType')
    water_quantity=models.FloatField(default=0)
    def __unicode__(self):
        return self.sensor + ' ' + self.switch  

class Sensor(models.Model):
    node = models.CharField(max_length=3, primary_key=True)
    value = models.IntegerField(max_length=3)
    def __unicode__(self):
        return self.pinNumber + ' ' + self.status 
    
class Switch(models.Model):
    pinNumber = models.CharField(max_length=3, primary_key=True)
    status = models.IntegerField(default=0)
    def __unicode__(self):
        return self.pinNumber + ' ' + self.status 
    
class SimpleSchedule(models.Model):
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(max_length=3)
    zone = models.ForeignKey('Zone')
    status = models.CharField(max_length=10, default='stopped')
    def __unicode__(self):
        return self.enabled + ' ' + self.zone 
    
class RepeatableSchedule(models.Model):
    name = models.CharField(max_length=20)
    day = models.CharField(max_length=10)
    time = models.TimeField()
    duration = models.IntegerField(max_length=3)
    zone = models.ForeignKey('Zone')
    status = models.CharField(max_length=10, default='stopped')  
    def __unicode__(self):
        return self.enabled + ' ' + self.zone  
    
class IrrigationHistory(models.Model):
    zone_id = models.ForeignKey('Zone')
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
    day_number = models.IntegerField(max_length=3, primary_key=True)
    kc_value = models.FloatField(max_length=4)
    irrigation_required = models.BooleanField(default=False)
    runtime = models.IntegerField(max_length=3,default=0)
    water_mm = models.FloatField(max_length=3,default=0)
    def __unicode__(self):
        return self.day_number
    
class IrrigationTemplate(models.Model):
    day_counter = models.IntegerField(max_length=3)
    name = models.CharField(max_length=15)
    def __unicode__(self):
        return self.template
   
class IrrigationSettings(models.Model):
    id = models.IntegerField(max_length=1, primary_key=True)
    flow_meter = models.IntegerField(default=0)
    running_zones = models.IntegerField(default=0)
    evapotranspiracy = models.FloatField(default=0)
    cost_perLiter = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    water = models.FloatField(default=0)
    runnable_zones_number=models.IntegerField(default=1)
    def __unicode__(self):
        return self.pump
    
class Pump(models.Model):
    id = models.IntegerField(max_length=1, primary_key=True)
    switch = models.ForeignKey('Switch')
    up_time = models.IntegerField(default=0)
    run_limit = models.IntegerField(default=1)
    down_time = models.IntegerField(default=0)
    stop_limit = models.IntegerField(default=1)

class SoilType(models.Model):
    name = models.CharField(max_length=20)
    value = models.FloatField(default=0)
    
class TaskQueue(models.Model):
    zone_id=models.ForeignKey('Zone')
    seq_number=models.IntegerField(default=0)
    