#For parsing Arduino data
import re

#For communication with Arduino
import serial 

#for communication with Server
import requests
import json
#import numpy as np
import datetime
import time

def main():
    baseurl = 'https://netfridge-jgilles.c9users.io/'
    # 
    # Send the data to the server
    #
    # Set url address.
    base = baseurl
    # Set query (i.e. http://url.com/?key=value).
    query = {}
    # Set header.
    header = {'Content-Type':'application/json'}
    print "Send:",
    # Generature UNIX timestamps for each data point
    at = int(1449194700)
    
    # Send Compressor State
    q = 11
    endpoint = 'network/Demo/object/Waves/stream/CompressorState'
    payload = [ {'value':q,'at':at } ]
    print q
    # Set body (also referred to as data or payload). Body is a JSON string.
    body = json.dumps(payload)
    # Form and send request. Set timeout to 2 minutes. Receive response.
    r = requests.request('post', base + endpoint, data=body, params=query, headers=header, timeout=10 )
    print r    
    
main()