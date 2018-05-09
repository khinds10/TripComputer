#!/usr/bin/python
# Trip Computer - Dual Display Dashboard Trip Computer
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
from socket import AF_INET, SOCK_DGRAM
import datetime as dt
from math import cos, sin, pi, radians
import cgi, json, re, socket, string, struct, subprocess, sys, time, urllib2
import includes.data as data
import info.CurrentReadings as CurrentReadings
import info.WeatherDetails as WeatherDetails
import info.GPSInfo as GPSInfo
import info.Wifi as Wifi
import info.Notification as Notification

# setup the commands to drive the left and right screens
leftDisplayCommand = "/home/pi/TripComputer/computer/left-display"
rightDisplayCommand = "/home/pi/TripComputer/computer/right-display"

# start logging wifi status
data.removeJSONFile('wifi.data')

def getNTPTime(host = "pool.ntp.org"):
    ''' get time from the global NTP protocol '''
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'

    # reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800L # 1970-01-01 00:00:00

    # connect to server
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.settimeout(2)
    client.sendto(msg, address)
    msg, address = client.recvfrom( buf )

    t = struct.unpack( "!12I", msg )[10]
    t -= TIME1970
    return time.ctime(t).replace("  "," ")

def setupRightScreen():
    ''' setup initial right hand screen '''
    subprocess.call([rightDisplayCommand, "clear"])
    subprocess.call([rightDisplayCommand, "setColor", "255"])
    subprocess.call([rightDisplayCommand, "setFont", "18"])
    subprocess.call([rightDisplayCommand, "Temp","10","10"])
    subprocess.call([rightDisplayCommand, "Driving","10","40"])
    subprocess.call([rightDisplayCommand, "Calendar","10","100"])
    subprocess.call([rightDisplayCommand, "Speed","10","70"])
    subprocess.call([rightDisplayCommand, "Traffic","100","70"])
    
def setupLeftScreen():
    ''' setup initial left hand screen '''
    subprocess.call([leftDisplayCommand, "clear"])
    subprocess.call([leftDisplayCommand, "setColor", "255"])
    subprocess.call([leftDisplayCommand, "setFont","18"])
    subprocess.call([leftDisplayCommand, "GPS","3","10"])
    subprocess.call([leftDisplayCommand, "setColor","255"])
    subprocess.call([leftDisplayCommand, "NoWifi","105","10"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","38","0"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","37","0"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","36","0"])

drivingTime = ''
def updateDrivingTime(timeNew):
    ''' update time driving '''
    global drivingTime
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "52", drivingTime])
    subprocess.call([rightDisplayCommand, "setColor", "255"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "52", timeNew])
    drivingTime = timeNew

dailyDrivingTime = ''
def updateDailyDrivingTime(timeNew):
    ''' update time driving '''
    global dailyDrivingTime
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "113", dailyDrivingTime])
    subprocess.call([rightDisplayCommand, "setColor", "255"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "113", timeNew])
    dailyDrivingTime = timeNew

milesDrivenAmount = ''
def updateAvgMPH(milesDrivenNew):
    ''' update time driving '''
    global milesDrivenAmount
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "83", milesDrivenAmount])
    subprocess.call([rightDisplayCommand, "setColor", "222"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "83", milesDrivenNew])
    milesDrivenAmount = milesDrivenNew

percentTrafficAmount = ''
def updatePercentTraffic(percentTrafficNew):
    ''' update percent time in traffic '''
    global percentTrafficAmount
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "122", "83", percentTrafficAmount])
    subprocess.call([rightDisplayCommand, "setColor", "254"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "122", "83", percentTrafficNew])
    percentTrafficAmount = percentTrafficNew

indoorTempAmount = ''
outdoorTempAmount = ''
def updateTemps(indoorTempNew, outdoorTempNew):
    ''' update indoor and outdoor temps '''
    global indoorTempAmount, outdoorTempAmount
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "22", indoorTempAmount])
    subprocess.call([rightDisplayCommand, "setColor", "250"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "35", "22", indoorTempNew])
    subprocess.call([rightDisplayCommand, "setColor", "0"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "80", "22", outdoorTempAmount])
    subprocess.call([rightDisplayCommand, "setColor", "223"])
    subprocess.call([rightDisplayCommand, "printxy_abs", "80", "22", outdoorTempNew])
    indoorTempAmount = indoorTempNew
    outdoorTempAmount = outdoorTempNew

compassDirectionCurrent = ''
def updateDirection(compassDirectionNew):
    ''' update direction headed '''
    global compassDirectionCurrent
    subprocess.call([leftDisplayCommand, "setColor", "0"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "20", "23", compassDirectionCurrent])
    subprocess.call([leftDisplayCommand, "setColor", "249"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "20", "23", compassDirectionNew])
    compassDirectionCurrent = compassDirectionNew

def updateSpecialMessage(newSpecialMessage):
    ''' update direction headed '''
    subprocess.call([leftDisplayCommand, "setColor", "0"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "5", "120", '             '])
    subprocess.call([leftDisplayCommand, "setColor", "255"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "5", "120", newSpecialMessage])

def getTimeDriving():
    ''' update time driving from uptime command'''
    uptime = subprocess.check_output(['uptime', '-p'])
    uptime = re.sub("up ",'',uptime)
    uptime = re.sub(" minutes",'m',uptime)
    uptime = re.sub(" minute",'m',uptime)
    uptime = re.sub(" hours",'h',uptime)
    uptime = re.sub(" hour",'h',uptime)
    uptime = re.sub(", ",'',uptime)
    return uptime.rstrip()
    
def percentage(part, whole):
    '''get percent as a float'''
    return 100 * float(part)/float(whole)
        
def timeStringToMinutes(timeString):
    '''break down the string such as "2h4m" to just minutes as integer'''

    # extract minutes
    try:
        timeStringMinutes = re.findall("[0-9]+m", timeString)
        if timeStringMinutes[0]:
            timeStringMinutes[0] = re.sub("m",'',timeStringMinutes[0])
            timeStringMinutes = int(timeStringMinutes[0])
    except:
        timeStringMinutes = 0

    # extract hours
    try:
        timeStringHours = re.findall("[0-9]+h", timeString)
        if timeStringHours[0]:
            timeStringHours[0] = re.sub("h",'',timeStringHours[0])
            timeStringHours = int(timeStringHours[0])
    except:
        timeStringHours = 0
    
    # get the total minutes and return    
    return (int(timeStringHours) * 60) + int(timeStringMinutes)

def calculateInTrafficPercent(inTrafficTimeAmount, drivingTimeAmount):
    '''for given in traffic time and total driving time get the percent time in traffic as int'''
    inTrafficTotalMinutes = timeStringToMinutes(inTrafficTimeAmount)    
    drivingTotalMinutes = timeStringToMinutes(drivingTimeAmount)
    percent = int(percentage(inTrafficTotalMinutes, drivingTotalMinutes))
    return str(percent)

def toggleWifiIcon():
    ''' toggle wifi icon based on if we have a valid ping from google or not and log that to file for other processes '''    
    global isInternetConnected
    wifi = Wifi.Wifi()
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        subprocess.call([leftDisplayCommand, "Wifi","105","10"])
        wifi.isConnected = 'yes'
        data.saveJSONObjToFile('wifi.data', wifi)
        isInternetConnected = True
    except urllib2.URLError as err:
        subprocess.call([leftDisplayCommand, "NoWifi","105","10"])
        wifi.isConnected = 'no'
        data.saveJSONObjToFile('wifi.data', wifi)
        isInternetConnected = False

def checkTimeCorrect():
    ''' check if indeed the local time on the RPi is set according to internet time '''

    try: 
        timeIsSet = True
        internetTime = getNTPTime().split()
        localTime = subprocess.check_output(['date']).split()

        # check date is correct
        internetTimeSet = internetTime[3].split(':')
        localTimeSet = localTime[3].split(':')
        if internetTime[0] != localTime[0]:
            timeIsSet = False
        if internetTime[2] != localTime[1]:
            timeIsSet = False
            
        # check clock is correct
        internetTimeSet = internetTime[3].split(':')
        localTimeSet = localTime[3].split(':')
        if internetTimeSet[0] != localTimeSet[0]:
            timeIsSet = False
        if internetTimeSet[1] != localTimeSet[1]:
            timeIsSet = False
    except:
        timeIsSet = False
    return timeIsSet

def setCompass(x,y, color):
    ''' for x,y direction coordinates and color draw the compass with needle '''
    subprocess.call([leftDisplayCommand, "setColor", "255"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","38","0"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","37","0"])
    subprocess.call([leftDisplayCommand, "drawCircle","75","60","36","0"])
    subprocess.call([leftDisplayCommand, "setColor", color])
    subprocess.call([leftDisplayCommand, "drawLine", "77", "62", str(x), str(y)])
    subprocess.call([leftDisplayCommand, "drawLine", "76", "61", str(x), str(y)])        
    subprocess.call([leftDisplayCommand, "drawLine", "75", "60", str(x), str(y)])
    subprocess.call([leftDisplayCommand, "drawLine", "74", "59", str(x), str(y)])
    subprocess.call([leftDisplayCommand, "drawLine", "73", "58", str(x), str(y)])




def scrollCurrentPhoneNotification():
    ''' scroll throught the current message in the special message window '''
    global currentPhoneMessage, currentScrolledPosition, scrolledTextLength, timesScrolled
    totalScrollCharLength = len(list(currentPhoneMessage)) / scrolledTextLength + 1
    
    # scroll message at current position we're in
    if currentScrolledPosition == 0:
        updateSpecialMessage(currentPhoneMessage[0:13])    
    else:
        textStart = currentScrolledPosition*13
        updateSpecialMessage(currentPhoneMessage[textStart:textStart+13])
    currentScrolledPosition = currentScrolledPosition + 1
    
    if currentScrolledPosition > totalScrollCharLength:
        currentScrolledPosition = 0
        timesScrolled = timesScrolled + 1
        
    if timesScrolled > 3:
        timesScrolled = 0
        scrollCurrentMessage = False

# begin computer
setupRightScreen()
setupLeftScreen()
secondsPassed = 0
timeIsCorrect = False
southPX = 0
southPY = 0
northPX = 0
northPY = 0
currentDirection = 0
currentDirectionPrevious = 0
isInternetConnected = False

# current phone message and flag if it should be scrolling through it or not
prevPhoneMessage = ''
currentPhoneMessage = ''
scrollCurrentMessage = False
currentScrolledPosition = 0
timesScrolled = 0
scrolledTextLength = 13

while True:

    # if flag set then scroll through current message
    if scrollCurrentMessage:
         scrollCurrentPhoneNotification()

    # each 10 seconds loop
    if (secondsPassed % 10 == 0):
        toggleWifiIcon()
       
        # update inside tempurature data
        tempInfo = data.getJSONFromDataFile('temp.data')
        if tempInfo == "":
            tempInfo = CurrentReadings.CurrentReadings()
            tempInfo = json.loads(tempInfo.to_JSON())
    
        # get outside weather info
        weatherInfo = data.getJSONFromDataFile('weather.data')
        if weatherInfo == "":
            weatherInfo = WeatherDetails.WeatherDetails()
            weatherInfo = json.loads(weatherInfo.to_JSON())

        # update inside and outside weather
        insideTemp = str(tempInfo['temp']) + "f"
        if int(tempInfo['temp']) == 0:
            insideTemp = "--f"
        outsideTemp = str(int(weatherInfo['apparentTemperature'])) + "f"
        if int(weatherInfo['apparentTemperature']) == 0:
            outsideTemp = "     "
        else:
            outsideTemp = "(" + outsideTemp + ")"
        updateTemps(insideTemp,outsideTemp)
        
        # get current driving stats
        drivingStatistics = data.getJSONFromDataFile('stats.data')
        if drivingStatistics == "":
            drivingStatistics = DrivingStatistics.DrivingStatistics()
            drivingStatistics = json.loads(tempInfo.to_JSON())

        # average speed
        updateAvgMPH(str(drivingStatistics['averageSpeeds'][0]) + 'mph')
        
        # current driving time / miles travelled
        uptime = getTimeDriving()
        updateDrivingTime(str(uptime) + ' - ' + str(drivingStatistics['milesTravelled'][0]) + 'mi')
        updateDailyDrivingTime(str(drivingStatistics['drivingTimes'][1]) + ' - ' + str(drivingStatistics['milesTravelled'][1]) + 'mi')
        
        # current in-traffic time
        currentInTraffic = str(drivingStatistics['inTrafficTimes'][0])
        updatePercentTraffic(calculateInTrafficPercent(str(currentInTraffic), str(uptime)) + '%')
        
        #        #if currentPhoneMessage

        #        # check time against internet
        #        if timeIsCorrect == False:
        #            timeIsCorrect = checkTimeCorrect()

        #        if timeIsCorrect:
        #            updateSpecialMessage(dt.datetime.now().strftime('%I:%M%p %m/%d'))
        #        else:
        #            updateSpecialMessage('             ')
        
        # update new phone notification if set and internet connected      
        if isInternetConnected:
            notificationInfo = data.getJSONFromDataFile('notification.data')

            if notificationInfo == "":
                notificationInfo = Notification.Notification()
                notificationInfo = json.loads(tempInfo.to_JSON())

            # new message found, get the scroller going
            if notificationInfo['message'] != prevPhoneMessage:
                currentPhoneMessage = notificationInfo['message']
                scrollCurrentMessage = True    
                currentScrolledPosition = 0
                prevPhoneMessage = currentPhoneMessage

    # each 2 seconds loop
    if (secondsPassed % 2 == 0):
    
        # get current direction heading
        locationInfo = data.getJSONFromDataFile('location.data')

        # calculate line angle from GPS degrees convert to radians, but only if we're actually moving more than 5mph
        if locationInfo != "":
            if (int(locationInfo['speed']) > 5):
        
                currentDirection = locationInfo['track']                
                if currentDirection != currentDirectionPrevious:

                    # update direction headed
                    updateDirection(str(data.getHeadingByDegrees(currentDirection)))

                    # clear heading
                    setCompass(southPX, southPY, "0")
                    setCompass(northPX, northPY, "0")

                    # radians based on where true north is
                    r = radians(360 - currentDirection)
                    radius = 38

                    # show south
                    southPX = round(75 - radius * sin(r))
                    southPY = round(60 + radius * cos(r))
                    setCompass(southPX, southPY, "255")

                    # show north
                    northPX = round(75 + radius * sin(r))
                    northPY = round(60 - radius * cos(r))
                    setCompass(northPX,northPY, "224")
                    currentDirectionPrevious = currentDirection

        else:
            updateDirection("    ")
        
    secondsPassed = secondsPassed + 1
    time.sleep(1)
