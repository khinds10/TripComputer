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
previousMessage = "Welcome to Kevin's Car"

def checkForMessage():
    """check for new messages"""
    incomingMessage = json.loads(unicode(subprocess.check_output(['curl', settings.dashboardServer + "/message"]), errors='ignore'))
    message = str(incomingMessage["message"])
    message = message[:maxMessageLength]

def saveMessageToFile(message):
    """save new notification message to file for gauge to display"""
    notification = Notification.Notification()
    data.saveJSONObjToFile('notification.data', notification)
    
# save the initial welcome message
saveMessageToFile(previousMessage)

# each 5 seconds check for new messages
while True:
    try:
        # if message has changed, then save the new one to the file
        checkForMessage()
        if (previousMessage != message):
            saveMessageToFile(message)
            previousMessage = message  
    
    except (Exception):
        pass
    time.sleep(5)

