"""
WSGI config for IrrigationApp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IrrigationApp.settings")


import paho.mqtt.client as mqtt
from IrrigationApp.shared import addTaskToQueue, deleteTaskFromQueue

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("irrigationapp/control")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    reader = codecs.getreader("utf-8")
    js = json.load(reader(str(msg.payload)))
    
    zone = js['zone']
    status = js['status']
    mZone = Zone.objects.get(id=zone)
    if status == '1':    
        addTaskToQueue(mZone)
    else :
        deleteTaskFromQueue(mZone)
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("iot.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()



from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


