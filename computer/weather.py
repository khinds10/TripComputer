#!/usr/bin/python
# Get current forecast from forecast.io using lat/long
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import time, json, string, cgi, subprocess
import includes.data as data
import includes.settings as settings
import info.WeatherDetails as WeatherDetails

# remove old file and start logging weather
data.removeJSONFile('weather.data')
while True:
    try:
    
        # get current location from GPS
        currentLocationInfo = data.getLastKnownLatLong()
                
        # get current forecast from location
        weatherInfo = json.loads(subprocess.check_output(['curl', 'https://api.forecast.io/forecast/' + settings.weatherAPIKey + '/' + str(currentLocationInfo['latitude']) + ',' + str(currentLocationInfo['longitude']) + '?lang=en']))
        hourlyConditions = weatherInfo['minutely']
        currentConditions = weatherInfo['currently']
        
        # gather info in serializable object to store as JSON file
        weatherDetails = WeatherDetails.WeatherDetails()
        weatherDetails.time = int(currentConditions['time'])
        weatherDetails.summary = str(currentConditions['summary'])
        weatherDetails.nextHour = str(hourlyConditions['summary'])
        weatherDetails.icon = str(currentConditions['icon'])
        weatherDetails.apparentTemperature = float(currentConditions['apparentTemperature'])
        weatherDetails.humidity = float(currentConditions['humidity'])
        weatherDetails.precipIntensity = float(currentConditions['precipIntensity'])
        weatherDetails.precipProbability = float(currentConditions['precipProbability'])
        weatherDetails.windSpeed = float(currentConditions['windSpeed'])

        # set to not precipitating by default
        weatherDetails.isPrecip = False
        weatherDetails.precipStopping = False
        weatherDetails.precipStarting = False
        weatherDetails.solidPrecip = False
        weatherDetails.minute = 0
        
        # get if it's going to have precip or not        
        for precipCheck in hourlyConditions['data']:
            if (float(precipCheck['precipProbability']) > 0.29):
                weatherDetails.isPrecip = True

        # get if the rain is already started or starting soon
        if weatherDetails.isPrecip and (float(hourlyConditions['data'][0]['precipProbability']) > 0.29):
            weatherDetails.precipStopping = True
        elif weatherDetails.isPrecip:
            weatherDetails.precipStarting = True

        # get the moment that the precip will stop or start at
        for precipCheck in hourlyConditions['data']:
            if weatherDetails.precipStarting and (float(precipCheck['precipProbability']) > 0.29):
                break
            if weatherDetails.precipStopping and (float(precipCheck['precipProbability']) < 0.29):
                break
            weatherDetails.minute = weatherDetails.minute + 1

        # if we've went through the whole hour, then it's solid precip
        if weatherDetails.isPrecip and (weatherDetails.minute > 59):
            weatherDetails.solidPrecip = True

        # create or rewrite data to weather data file as JSON, then wait 5 minutes
        data.saveJSONObjToFile('weather.data', weatherDetails)
        time.sleep(300)
        
    except (Exception):
    
        # GPS is not fixed or network issue, wait 30 seconds
        time.sleep(30)
