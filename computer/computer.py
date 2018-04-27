#!/usr/bin/python
# Trip Computer - Dual Display Dashboard Trip Computer
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
from socket import AF_INET, SOCK_DGRAM
import datetime as dt
import cgi, json, re, socket, string, struct, subprocess, sys, time, urllib2
import includes.data as data
import info.CurrentReadings as CurrentReadings
import info.WeatherDetails as WeatherDetails
import info.GPSInfo as GPSInfo

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


## weather.data
#weatherNextHour = ''
#weatherOutside = ''

## temp.data
#tempHmidty = ''

## location.data  (use equation)
#locationTrack = ''
#currentTime = ''

## stats.data (get the first of each)
#statsDrivingTimes = ''
#statsInTrafficTimes = ''
#statsAverageSpeeds = ''
#statsMilesTravelled = ''

## current time
#timeNow = ''

## reset screen and load beginning driving statistics using the configured digole driver
#digoleDriveLocation = "/home/pi/TripComputer/computer/digole"
#resetScreen()

#########################
## default screen
#########################

## begin loop through main default screen
#while True:
#    try:
#        # weather.data
#        weatherInfo = data.getJSONFromDataFile('weather.data')
#        if weatherInfo == "":
#            weatherInfo = WeatherDetails.WeatherDetails()
#            weatherInfo = json.loads(weatherInfo.to_JSON())

#        # next hour weather
#        if weatherNextHour != weatherInfo['nextHour']:
#            printByFontColorPosition("51", "255", "5", "75", weatherInfo['nextHour'][:25], weatherNextHour)
#            weatherNextHour = weatherInfo['nextHour']

#        # outside temp/humidity
#        weatherOutsideUpdated = '[' + str(int(weatherInfo['apparentTemperature'])) + '*F ' + str(int(weatherInfo['humidity']*100)) + '%]'
#        if weatherOutside != weatherOutsideUpdated:
#            printByFontColorPosition("120", "240", "150", "35", weatherOutsideUpdated, weatherOutside)
#            weatherOutside = weatherOutsideUpdated
#        
#        # temp.data
#        tempInfo = data.getJSONFromDataFile('temp.data')
#        if tempInfo == "":
#            tempInfo = CurrentReadings.CurrentReadings()
#            tempInfo = json.loads(tempInfo.to_JSON())
#        
#        # inside temp / humidity
#        tempHmidtyUpdated =  str(tempInfo['temp']) + "*F " + str(tempInfo['hmidty']) + "%"
#        if tempHmidty != tempHmidtyUpdated:
#            printByFontColorPosition("120", "249", "5", "35", tempHmidtyUpdated, tempHmidty)        
#            tempHmidty = tempHmidtyUpdated

#        # stats.data
#        drivingStatistics = data.getJSONFromDataFile('stats.data')
#        if drivingStatistics == "":
#            drivingStatistics = DrivingStatistics.DrivingStatistics()
#            drivingStatistics = json.loads(tempInfo.to_JSON())
#        
#        # current driving time
#        statsDrivingTimesUpdated = str(drivingStatistics['drivingTimes'][0])
#        if statsDrivingTimes != statsDrivingTimesUpdated:
#            printByFontColorPosition("120", "28", "5", "125", statsDrivingTimesUpdated, statsDrivingTimes)
#            statsDrivingTimes = statsDrivingTimesUpdated
#            
#        # current in-traffic time
#        statsInTrafficTimesUpdated = str(drivingStatistics['inTrafficTimes'][0]) + ' [Traffic]'
#        if statsInTrafficTimes != statsInTrafficTimesUpdated:
#            printByFontColorPosition("120", "252", "120", "125", statsInTrafficTimesUpdated, statsInTrafficTimes)
#            statsInTrafficTimes = statsInTrafficTimesUpdated
#        
#        # average speed
#        statsAverageSpeedsUpdated = str(drivingStatistics['averageSpeeds'][0]) + 'mph [Avg]'
#        if statsAverageSpeeds != statsAverageSpeedsUpdated:
#            printByFontColorPosition("120", "250", "5", "175", statsAverageSpeedsUpdated, statsAverageSpeeds)
#            statsAverageSpeeds = statsAverageSpeedsUpdated

#        # miles travelled
#        statsMilesTravelledUpdated = str(drivingStatistics['milesTravelled'][0]) + ' mi Est.'
#        if statsMilesTravelled != statsMilesTravelledUpdated:
#            printByFontColorPosition("120", "222", "190", "175", statsMilesTravelledUpdated[:10], statsMilesTravelled)
#            statsMilesTravelled = statsMilesTravelledUpdated
#        
#        # location.data
#        locationInfo = data.getJSONFromDataFile('location.data')
#        if locationInfo == "":
#            locationInfo = GPSInfo.GPSInfo()
#            locationInfo = json.loads(locationInfo.to_JSON())

#        # TODO, have a is the GPS fixed yet since reboot to then show the time because we have it then
#        gpsFix = 'no'
#        
#        gpsFix = 'yes'
#        if gpsFix == "ok":
#            timeUpdated = " - " + dt.datetime.now().time().strftime('%I:%M%p').lstrip('0') + " - "
#        else:
#            timeUpdated = "             "
#            
#        if timeNow != timeUpdated:
#            printByFontColorPosition("120", "249", "150", "225", timeUpdated, timeNow)
#            timeNow = timeUpdated

#    except:
#        pass
#    time.sleep(1)




##!/usr/bin/python
## Show on/off indicator lights for if internet connected and if GPS location found
## Kevin Hinds http://www.kevinhinds.com
## License: GPL 2.0
#import time, subprocess, urllib2
#import RPi.GPIO as GPIO
#import includes.data as data

## to use Raspberry Pi board pin numbers  
#GPIO.setmode(GPIO.BOARD)
# 
## set up GPIO output channel
#GPIO.setup(13, GPIO.OUT)
#GPIO.output(13,GPIO.LOW)
#GPIO.setup(15, GPIO.OUT)
#GPIO.output(15,GPIO.LOW)
#GPIO.setup(16, GPIO.OUT)
#GPIO.output(16,GPIO.LOW)

#def setLight(pin, isLit):
#    """ set light to on or off based on boolean value """
#    if isLit:
#        GPIO.output(pin,GPIO.HIGH)
#    else:
#        GPIO.output(pin,GPIO.LOW)

#def checkInternetOn():
#    """ set internet connected light by ability to connect to google or not """
#    try:
#        urllib2.urlopen('http://www.kevinhinds.net', timeout=1)
#        setLight(13, 1)
#    except urllib2.URLError as err: 
#        setLight(13, 0)

## turn on and off indicator lights based on GPS and Internet connectivity
#while True:
#    try:

#        # check internet connection
#        checkInternetOn()

#        # check GPS status and turn on light if no issues
#        currentLocationInfo = data.getCurrentLatLong()
#        setLight(15, 1)
#        
#    except (Exception):
#        # GPS issue, turn off light
#        setLight(15, 0)
#    
#    time.sleep(1)


##!/usr/bin/python
## Show current travel direction as compass reading to ssd1306 display
## @author khinds
## @license http://opensource.org/licenses/gpl-license.php GNU Public License
#from math import cos, sin, pi, radians
#from oled.device import ssd1306, sh1106
#from oled.render import canvas
#from PIL import ImageFont
#import time
#import includes.data as data
# 
## define fonts
#font = ImageFont.load_default()
#titleFont = ImageFont.truetype('/home/pi/TripComputer/computer/fonts/DroidSansMono.ttf', 20)
#bodyFont = ImageFont.truetype('/home/pi/TripComputer/computer/fonts/TheNextFont.ttf', 24)

## device and screen settings
#device = ssd1306()
#currentDirection = 0
#while True:
#    try:
#        with canvas(device) as draw:
#        
#            # location.data
#            locationInfo = data.getJSONFromDataFile('location.data')
#            if locationInfo != "":
#                # calculate line angle from GPS degrees convert to radians, but only if we're moving more than 5mph
#                if (int(locationInfo['speed']) > 5):
#                    currentDirection = locationInfo['track']
#                draw.text((70, 2), str(int(currentDirection)) + "*", font=titleFont, fill=255)
#                draw.text((70, 40), str(data.getHeadingByDegrees(currentDirection)), font=bodyFont, fill=255)
#                draw.ellipse((2, 2 , 60, 60), outline=255, fill=0)       
#                r = radians(currentDirection)
#                radius = 30
#                px = round(32 + radius * sin(r))
#                py = round(32 - radius * cos(r))
#                draw.line((32, 32, px, py), fill=255)
#            else:
#                draw.text((10, 5), str('GPS'), font=titleFont, fill=255)
#                draw.text((10, 30), str('Searching'), font=titleFont, fill=255)
#    except:
#        with canvas(device) as draw:
#            draw.text((10, 5), str('GPS'), font=titleFont, fill=255)
#            draw.text((10, 30), str('Searching'), font=titleFont, fill=255)
#    time.sleep(1)

