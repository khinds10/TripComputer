#!/usr/bin/python
# Current Phone Notification
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import json
class Notification:
    '''Phone Notification as class to persist as JSON information to file'''
    message = ''
    
    def __init__(self):
        self.message = ''

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
