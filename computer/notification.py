#!/usr/bin/python
# Get local temp from DHT11 humidistat 
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import Adafruit_DHT
import os, time, json, string, cgi, subprocess
import includes.data as data
import info.Notification as Notification
import includes.settings as settings

# start logging notifications
data.removeJSONFile('notification.data')
previousMessage = "Welcome to   Kevin's Car"
firstRun = True

def checkForMessage():
    """check for new messages"""
    incomingMessage = json.loads(unicode(subprocess.check_output(['curl', settings.dashboardServer + "/message"]), errors='ignore'))
    return str(incomingMessage["message"])

def saveMessageToFile(message):
    """save new notification message to file for gauge to display"""
    notification = Notification.Notification()
    notification.message = message
    data.saveJSONObjToFile('notification.data', notification)
    
# save the initial welcome message
saveMessageToFile(previousMessage)

# each 5 seconds check for new messages
while True:
    try:
        # if we're running the first time, no need to display an old message I already have read
        if (firstRun):
            previousMessage = checkForMessage()
        else:
            # if message has changed, then save the new one to the file
            message = checkForMessage()
            if (previousMessage != message):
                saveMessageToFile(message)
                previousMessage = message  
    except (Exception):
        # internet connectivity issue, just pass
        pass
    firstRun = False
    time.sleep(5)

