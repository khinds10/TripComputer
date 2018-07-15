#!/usr/bin/python
# Log to database the current readings for all known info each second as you're driving
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import os, time, json
import includes.data as data
import includes.postgres as postgres
import info.CurrentReadings as CurrentReadings
import info.WeatherDetails as WeatherDetails
import info.GPSInfo as GPSInfo
import info.CurrentReadings as CurrentReadings
import info.LocaleDetails as LocaleDetails

# save full datasets to DB each second
while True:
    try:
        locationInfo = data.getJSONFromDataFile('gps.data')
        print locationInfo
        if locationInfo == "":
            locationInfo = GPSInfo.GPSInfo()
            locationInfo = json.loads(locationInfo.to_JSON())
        
        localeInfo = data.getJSONFromDataFile('address.data')
        print localeInfo
        if localeInfo == "":
            localeInfo = LocaleDetails.LocaleDetails()
            localeInfo = json.loads(localeInfo.to_JSON())
        
        tempInfo = data.getJSONFromDataFile('temp.data')
        print tempInfo
        if tempInfo == "":
            tempInfo = CurrentReadings.CurrentReadings()
            tempInfo = json.loads(tempInfo.to_JSON())
        
        weatherInfo = data.getJSONFromDataFile('weather.data')
        print weatherInfo
        if weatherInfo == "":
            weatherInfo = WeatherDetails.WeatherDetails()
            weatherInfo = json.loads(weatherInfo.to_JSON())
            
        postgres.saveDrivingStats(locationInfo, localeInfo, tempInfo, weatherInfo)

    except (Exception):
        pass
    time.sleep(1)
