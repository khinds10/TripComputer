#!/usr/bin/python
# Upload periodically latest driving stats to a central DB for analytics
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import os, time, json, string, cgi, subprocess, datetime
import includes.settings as settings
import includes.postgres as postgres


print settings.dashboardServer + '/upload.php?action=sync'

# sync local driving DB data to remote DB each 5 minutes
currentSyncInfo = json.loads(subprocess.check_output(['curl', settings.dashboardServer + '/upload.php?action=sync' ]))

print currentSyncInfo

fromTime = datetime.datetime.now().strftime('%Y-%m-%d 07:00:00')

fromTime = '2018-05-30 15:41:45'



print postgres.getResultsToUpload(fromTime)





#while True:

    #try:
    
    # if internet is connected
    
        # get the latest timestamp from the central db
            # adjust it for being UTC    
        
        # upload ALL the new rows in the driving_stats to it
    
    #except (Exception):
    #    pass
    #time.sleep(300)
