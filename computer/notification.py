#!/usr/bin/python
# Get local temp from DHT11 humidistat 
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import Adafruit_DHT
import os, time, json
import includes.data as data
import info.Notification as Notification

# start logging notifications
data.removeJSONFile('notification.data')
while True:

    wifi = data.getJSONFromDataFile('wifi.data')
    if wifi['isConnected'] == 'yes':
        notification = Notification.Notification()
        notification.message = 'NEW message test NEW message test NEW message test'
        data.saveJSONObjToFile('notification.data', notification)
    time.sleep(5)
