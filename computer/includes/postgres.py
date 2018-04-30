#!/usr/bin/env python
# Postgres save driving stats from local data objects
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import time, commands, subprocess, re, psycopg2
from datetime import datetime

# postgresql connection
postgresConn = psycopg2.connect(database="driving_statistics", user="pi", password="password", host="127.0.0.1", port="5432")
dBCursor = postgresConn.cursor()

def startNewTrip():
    """start new trip entry in the DB"""
    dBCursor.execute("""INSERT INTO driving_stats (time, new_trip_start) VALUES (%s, %s)""", ("now()","now()",))
    postgresConn.commit()

def saveDrivingStats(locationInfo, localeInfo, tempInfo, weatherInfo):
    """save second worth of driving stats to the DB"""
    dBCursor.execute("""INSERT INTO driving_stats (time, gps_latitude, gps_longitude, gps_altitude, gps_speed, gps_climb, gps_track, locale_address, locale_area, locale_city, locale_county, locale_country, locale_zipcode, inside_temp, inside_hmidty, weather_time, weather_summary, weather_icon, weather_apparenttemperature, weather_humidity, weather_precipintensity, weather_precipprobability, weather_windspeed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", ("now()", str(locationInfo["latitude"]), str(locationInfo["longitude"]), str(locationInfo["altitude"]), str(locationInfo["speed"]), str(locationInfo["climb"]), str(locationInfo["track"]), str(localeInfo["address"]), str(localeInfo["area"]), str(localeInfo["city"]), str(localeInfo["country"]), str(localeInfo["county"]), str(localeInfo["zipcode"]), str(tempInfo["temp"]), str(tempInfo["hmidty"]), "now()", str(weatherInfo["summary"]), str(weatherInfo["icon"]), str(weatherInfo["apparentTemperature"]), str(weatherInfo["humidity"]), str(weatherInfo["precipIntensity"]), str(weatherInfo["precipProbability"]), str(weatherInfo["windSpeed"])))
    postgresConn.commit()

def getNewTripStartID():
    """get the highest DB row indentifier where a new trip starts"""
    return getOneResult("SELECT max(id) FROM driving_stats WHERE new_trip_start IS NOT NULL")
    
def getDrivingTimes(tripStartId):
    """get the driving times for current trip, day, week and month"""
    return [getOneResult("SELECT count(id) FROM driving_stats WHERE id > " + str(tripStartId)))]

def getInTrafficTimes(tripStartId):
    """get the driving times for current trip, day, week and month, gps_speed = 'NaN' or -1 means that GPS is not currently found"""
    return [getOneResult("SELECT count(id) FROM driving_stats WHERE gps_speed < 2 AND gps_speed != 'NaN' AND gps_speed > -1 AND id > " + str(tripStartId))]

def getAverageSpeeds(tripStartId):
    """get the average speed in mph for current trip, day, week and month, gps_speed = 'NaN' or -1 means that GPS is not currently found"""    
    return [getOneResult("SELECT AVG(gps_speed) FROM driving_stats WHERE id > " + str(tripStartId) + " AND gps_speed != 'NaN' AND gps_speed > -1")]

def getAverageAlt(tripStartId):
    """get the average speed in mph for current trip, day, week and month, gps_speed = 'NaN' or -1 means that GPS is not currently found"""    
    return [getOneResult("SELECT AVG(gps_altitude) FROM driving_stats WHERE id > " + str(tripStartId) + " AND gps_speed != 'NaN' AND gps_speed > -1")]

def getAllResults(query):
    """get results rows for query"""
    dBCursor.execute(query)
    results = dBCursor.fetchall()
    return results

def getOneResult(query):
    """get one result row for query"""
    dBCursor.execute(query)
    result = dBCursor.fetchone()
    return result[0]
