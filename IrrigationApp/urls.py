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
    
    url(r'getSystemStatus[/]?$', views.getSystemStatus, name='getSystemStatus'),
    url(r'showAddNewSegment[/]?$', views.showAddNewSegment, name='showAddNewSegment'),
    url(r'doAddNewSegment[/]?$', views.doAddNewSegment, name='doAddNewSegment'),
    
    url(r'showSimpleSchedule[/]?$', views.showSimpleSchedule, name='showSimpleSchedule'),
    url(r'doSimpleSchedule[/]?$', views.doSimpleSchedule, name='doSimpleSchedule'),
    url(r'showRepeatableSchedule[/]?$', views.showRepeatableSchedule, name='showRepeatableSchedule'),
    url(r'doRepeatableSchedule[/]?$', views.doRepeatableSchedule, name='doRepeatableSchedule'),
    
    url(r'.*', views.showLogin, name='showLogin'),
    
    
)
