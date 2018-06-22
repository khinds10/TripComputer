#!/usr/bin/python
# Upload periodically latest driving stats to a central DB for analytics
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import os, time, json, string, cgi, subprocess, datetime, calendar
import includes.settings as settings
import includes.postgres as postgres
import requests

# sync local driving DB data to remote DB each 5 minutes
while True:
    try:
        # get last known recorded timestamp from the central DB
        currentSyncInfo = json.loads(subprocess.check_output(['curl', settings.devicesServer + '/upload.php?action=sync&device=trip-computer' ]))

        # get the rows as a list of lists with the datetime converted to MYSQL friendly string
        postData = postgres.getResultsToUpload(currentSyncInfo['time'])
        insertRows = []
        for item in postData:
            insertRows.append([item[0].strftime('%Y-%m-%d %H:%M:%S'), item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

        # post data to distributed DB
        requests.post(settings.devicesServer + '/upload.php?action=upload&device=trip-computer', data = {'data' :  json.dumps(insertRows)})
        
    except (Exception):
        # GPS is not fixed or network issue, wait 30 seconds
        time.sleep(30)
    time.sleep(300)
