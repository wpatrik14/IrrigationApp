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
    url(r'showMoistureHistory[/]?$', views.showMoistureHistory, name='showMoistureHistory'),
    url(r'showWeatherHistory[/]?$', views.showWeatherHistory, name='showWeatherHistory'),
    
    url(r'getSystemStatus[/]?$', views.getSystemStatus, name='getSystemStatus'),
    url(r'showAddNewZone[/]?$', views.showAddNewZone, name='showAddNewZone'),
    url(r'doAddNewZone[/]?$', views.doAddNewZone, name='doAddNewZone'),
    url(r'showEditZone[/]?$', views.showEditZone, name='showEditZone'),
    url(r'checkZone[/]?$', views.doCheckZone, name='doCheckZone'),
    
    url(r'doEditZone[/]?$', views.doEditZone, name='doEditZone'),
    url(r'showAddSettings[/]?$', views.showAddSettings, name='showAddSettings'),
    url(r'doAddSettings[/]?$', views.doAddSettings, name='doAddSettings'),
    
    url(r'showSimpleSchedule[/]?$', views.showSimpleSchedule, name='showSimpleSchedule'),
    url(r'doSimpleSchedule[/]?$', views.doSimpleSchedule, name='doSimpleSchedule'),
    url(r'showRepeatableSchedule[/]?$', views.showRepeatableSchedule, name='showRepeatableSchedule'),
    url(r'doRepeatableSchedule[/]?$', views.doRepeatableSchedule, name='doRepeatableSchedule'),
    url(r'deleteSimpleSchedule[/]?$', views.deleteSimpleSchedule, name='deleteSimpleSchedule'),
    url(r'deleteRepeatableSchedule[/]?$', views.deleteRepeatableSchedule, name='deleteRepeatableSchedule'),
    
    #===========================================================================
    # url(r'showZoneTemplate[/]?$', views.showZoneTemplate, name='showZoneTemplate'),
    # url(r'showAddSoilType[/]?$', views.showAddSoilType, name='showAddSoilType'),
    # url(r'doAddSoilType[/]?$', views.doAddSoilType, name='doAddSoilType'),
    # url(r'doAddIrrigationTemplate[/]?$', views.doAddIrrigationTemplate, name='doAddIrrigationTemplate'),
    # url(r'showDeleteIrrigationTemplate[/]?$', views.showDeleteIrrigationTemplate, name='showDeleteIrrigationTemplate'),
    # url(r'doDeleteIrrigationTemplate[/]?$', views.doDeleteIrrigationTemplate, name='doDeleteIrrigationTemplate'),
    # url(r'showAddIrrigationTemplate[/]?$', views.showAddIrrigationTemplate, name='showAddIrrigationTemplate'),
    #===========================================================================
    
    #url(r'deleteTask[/]?$', views.deleteTask, name='deleteTask'),
    url(r'deleteZone[/]?$', views.deleteZone, name='deleteZone'),
    url(r'deleteIrrigationHistory[/]?$', views.deleteIrrigationHistory, name='deleteIrrigationHistory'),
    
    url(r'.*', views.showLogin, name='showLogin'),
    
    
)
