from django.conf.urls import patterns, include, url
from django.contrib import admin
from IrrigationApp import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'IrrigationApp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'showLogin[/]?$', views.showLogin, name='showLogin'),
    url(r'doLogin[/]?$', views.doLogin, name='doLogin'),
    url(r'showRegistration[/]?$', views.showRegistration, name='showRegistration'),
    url(r'doRegistration[/]?$', views.doRegistration, name='doRegistration'),
    url(r'doLogout[/]?$', views.doLogout, name='doLogout'),
    
    url(r'showWeatherStatus[/]?$', views.showWeatherStatus, name='showWeatherStatus'),
    url(r'showIrrigationHistory[/]?$', views.showIrrigationHistory, name='showIrrigationHistory'),
    
    url(r'getSystemStatus[/]?$', views.getSystemStatus, name='getSystemStatus'),
    url(r'showAddNewSegment[/]?$', views.showAddNewSegment, name='showAddNewSegment'),
    url(r'doAddNewSegment[/]?$', views.doAddNewSegment, name='doAddNewSegment'),
    url(r'showEditSegment[/]?$', views.showEditSegment, name='showEditSegment'),
    url(r'doEditSegment[/]?$', views.doEditSegment, name='doEditSegment'),
    url(r'showAddSettings[/]?$', views.showAddSettings, name='showAddSettings'),
    url(r'doAddSettings[/]?$', views.doAddSettings, name='doAddSettings'),
    url(r'showAddArduino[/]?$', views.showAddArduino, name='showAddArduino'),
    url(r'doAddArduino[/]?$', views.doAddArduino, name='doAddArduino'),
    url(r'showAddSoilType[/]?$', views.showAddSoilType, name='showAddSoilType'),
    url(r'doAddSoilType[/]?$', views.doAddSoilType, name='doAddSoilType'),
    
    url(r'showSimpleSchedule[/]?$', views.showSimpleSchedule, name='showSimpleSchedule'),
    url(r'doSimpleSchedule[/]?$', views.doSimpleSchedule, name='doSimpleSchedule'),
    url(r'showRepeatableSchedule[/]?$', views.showRepeatableSchedule, name='showRepeatableSchedule'),
    url(r'doRepeatableSchedule[/]?$', views.doRepeatableSchedule, name='doRepeatableSchedule'),
    url(r'deleteSimpleSchedule[/]?$', views.deleteSimpleSchedule, name='deleteSimpleSchedule'),
    url(r'deleteRepeatableSchedule[/]?$', views.deleteRepeatableSchedule, name='deleteRepeatableSchedule'),
    
    url(r'showAddIrrigationTemplate[/]?$', views.showAddIrrigationTemplate, name='showAddIrrigationTemplate'),
    url(r'doAddIrrigationTemplate[/]?$', views.doAddIrrigationTemplate, name='doAddIrrigationTemplate'),
    url(r'showDeleteIrrigationTemplate[/]?$', views.showDeleteIrrigationTemplate, name='showDeleteIrrigationTemplate'),
    url(r'doDeleteIrrigationTemplate[/]?$', views.doDeleteIrrigationTemplate, name='doDeleteIrrigationTemplate'),
    
    url(r'showIrrigationTemplateValues[/]?$', views.showIrrigationTemplateValues, name='showIrrigationTemplateValues'),
    url(r'showAddIrrigationTemplate2[/]?$', views.showAddIrrigationTemplate2, name='showAddIrrigationTemplate2'),
    
    url(r'deleteTask[/]?$', views.deleteTask, name='deleteTask'),
    
    url(r'.*', views.showLogin, name='showLogin'),
    
    
)
