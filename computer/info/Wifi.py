#!/usr/bin/python
# Wifi Connection Status
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import json
class Wifi:
    '''Wifi connection status as class to persist as JSON information to file'''
    isConnected = 'no'
    
    def __init__(self):
        self.isConnected = 'no'

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
