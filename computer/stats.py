#!/usr/bin/python
# Summarize driving statistics to file once per minute
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import os, time, json
import includes.data as data
import includes.postgres as postgres
import info.Statistics as Statistics

# get the beginning of the trip
thisTripStartID = postgres.getNewTripStartID()

# remove stats data and start calculating
data.removeJSONFile('stats.data')

while True:
    try:
	    drivingStatistics = Statistics.Statistics()
	    drivingTimes = postgres.getDrivingTimes(thisTripStartID)
	    avgSpeeds = postgres.getAverageSpeeds(thisTripStartID)
	    drivingStatistics.drivingTimes = map(data.convertHumanReadable, drivingTimes)
	    drivingStatistics.inTrafficTimes = map(data.convertHumanReadable, postgres.getInTrafficTimes(thisTripStartID))
	    drivingStatistics.averageSpeeds = map(data.convertToString, map(data.convertToInt, avgSpeeds))
	    drivingStatistics.averageAltitude = map(data.convertToString, map(data.convertToInt, postgres.getAverageAlt(thisTripStartID)))
	    drivingStatistics.milesTravelled = [data.convertToInt(avgSpeeds[0]/60/60 * drivingTimes[0])]
            
	    # create or rewrite data to stats data file as JSON, then wait 1 minute
	    data.saveJSONObjToFile('stats.data', drivingStatistics)
	    time.sleep(60)

    except (Exception):
    
        # data issue, wait 5 seconds
        data.saveJSONObjToFile('stats.data', drivingStatistics)
        time.sleep(5)
