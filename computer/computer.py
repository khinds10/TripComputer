#!/usr/bin/python
# Trip Computer - Dual Display Dashboard Trip Computer
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
from socket import AF_INET, SOCK_DGRAM
import datetime as dt
import sys, socket, struct, time, urllib2, time, json, string, cgi, subprocess, json, re

# setup the commands to drive the left and right screens
leftDisplayCommand = "/home/pi/TripComputer/computer/left-display"
rightDisplayCommand = "/home/pi/TripComputer/computer/right-display"

def getNTPTime(host = "pool.ntp.org"):
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'

    # reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800L # 1970-01-01 00:00:00

    # connect to server
    client = socket.socket( AF_INET, SOCK_DGRAM)
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
    
currentTimeAmount = ''
def updateTimeOfDay(currentTimeNew):
    ''' update direction headed '''
    global currentTimeAmount
    subprocess.call([leftDisplayCommand, "setColor", "0"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "5", "120", currentTimeAmount])
    subprocess.call([leftDisplayCommand, "setColor", "255"])
    subprocess.call([leftDisplayCommand, "printxy_abs", "5", "120", currentTimeNew])
    currentTimeAmount = currentTimeNew

def updateTimeDriving():
    ''' update time driving from uptime command'''
    uptime = subprocess.check_output(['uptime', '-p'])
    uptime = re.sub("up ",'',uptime)
    uptime = re.sub(" minutes",'m',uptime)
    uptime = re.sub(" minute",'m',uptime)
    uptime = re.sub(" hours",'h',uptime)
    uptime = re.sub(" hour",'m',uptime)
    uptime = re.sub(", ",'',uptime)
    updateDrivingTime(uptime)
    
def toggleWifiIcon():
    ''' toggle wifi icon based on if we have a valid ping from google or not '''
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        subprocess.call([leftDisplayCommand, "Wifi","105","10"])
    except urllib2.URLError as err: 
        subprocess.call([leftDisplayCommand, "NoWifi","105","10"])
    
def checkTimeCorrect():
    ''' check if indeed the local time on the RPi is set according to internet time '''
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
    return timeIsSet

# begin computer
setupRightScreen()
setupLeftScreen()
secondsPassed = 0
while True:
    if (secondsPassed % 10 == 0):
        updateTimeDriving()
        toggleWifiIcon()
        
        # check time against internet
        timeSet = checkTimeCorrect()
        if timeSet:
            updateTimeOfDay(dt.datetime.now().strftime('%I:%M%p %m/%d'))
        else:
            updateTimeOfDay('')
            
        # check time against GPS @TODO

    secondsPassed = secondsPassed + 1
    time.sleep(1)

#updateDrivingTime('1h23m - 121mi')
#updateDailyDrivingTime('3h23m - 221mi')
#updateAvgMPH('23mph')
#updatePercentTraffic('15%')
#updateTemps('43f', '(23f)')
#updateDirection('NNE')
#updateTimeOfDay('10:35 am')

#time.sleep(3)
#updateDrivingTime('foo')
#updateDailyDrivingTime('bbb')
#updateAvgMPH('bar')
#updatePercentTraffic('fff')
#updateTemps('yyy', 'xxx')
#updateDirection('ZZZ')
#updateTimeOfDay('iiiiii')

#compass lines todo

#./left-display setColor 224
#./left-display drawLine 75 60 75 25
#./left-display setColor 255
#./left-display drawLine 75 60 75 95
