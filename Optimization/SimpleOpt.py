# -*- coding: utf-8 -*-
"""
Created on Tue Dec 08 00:35:51 2015

OPTIMIZATION ALGORYTHM

@author: Jordan
"""

#Optimization Algorythm
#For parsing Arduino data
import re

#For communication with Arduino
#import serial 

#for communication with Server
import requests as req
import requests
import json
import numpy as np
#import datetime as dt
from datetime import datetime
import datetime as DT
from calendar import timegm
import matplotlib.pyplot as plt
import time


#import things for pyiso

import pandas as pd
from pyiso import client_factory

CAISO = client_factory('CAISO')

# Run once at the start
def setup():
    try:     
        print "Setup"
    except:
        print "Setup Error"

def getWattTimeData():
    base = 'https://api.watttime.org/' 
    query = {}
    header = {'Authorization': 'Token 45ef728f3a69a73a5689df27c83680e8664bfde2'}
    endpoint = 'api/v1/marginal/?ba=CAISO&market=RT5M'
    address = base + endpoint
    query = {'limit':1000}
    r = requests.request('get', address, params=query, headers=header, timeout=120 )
    
    r2 = json.loads(r.text)
    
    #print r2    
    mC = np.zeros((12*24,1))
    for i in range(0,len(r2['results'])):
        t = r2['results'][i]['timestamp']
        carbonStructure = r2['results'][i]['marginal_carbon']
        if not(carbonStructure == None):
            margCarbon = carbonStructure['value']
            #print t
            readTime = time.strptime(t.replace('Z', 'GMT'),'%Y-%m-%dT%H:%M:%S%Z')
            unixT = timegm(readTime)
            ti = int(readTime.tm_hour*12 + round(readTime.tm_min/5))
            print t, unixT, ti, 'Carbon (lb/MW):',            
            print margCarbon
            #print mC
            #print ti
            if mC[ti] == 0:
                mC[ti] = margCarbon
    
    #print mC
    print mC.T
    for i in range(1,len(mC)):
        if mC[i] == 0:
            mC[i] = mC[i-1]
    for i in range(len(mC)-2,-1,-1):
        if mC[i] == 0:
            mC[i] = mC[i+1]
    print mC.T
    return mC

def getWTForecast():
    c = req.get('http://api.watttime.org/api/v1/current/', headers={'Authorization': 'Token 45ef728f3a69a73a5689df27c83680e8664bfde2'}, params={'ba': 'CAISO'})
    forecast_raw = c.json()[0]['forecast']
    current_raw = c.json()[0]['current']
    ci_forecast = np.zeros((24))
    for i in range(len(forecast_raw)):
        timestamp_UTC = DT.datetime.strptime(forecast_raw[i]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        timestamp = timestamp_UTC - DT.timedelta(hours=7) # Pacific Daylight Time (-6 for standard)
        ci_forecast[timestamp.hour] = forecast_raw[i]['marginal_carbon']['value']
    ci_forecast[DT.datetime.now().hour] = current_raw['marginal_carbon']['value']
    ci_forecast_ret = np.array([[i+24, ci_forecast[i]] for i in range(DT.datetime.now().hour - 24, DT.datetime.now().hour - 24 + len(forecast_raw))])
    return ci_forecast_ret

def getCostData():
    cost = np.zeros((12*24,1))
    for i in range(0,len(cost)):
        ti = i
        if ti < 5*12+30/5 or ti > 16*12+30/5:
            cost[ti] = 0.173
        else:
            cost[ti] = 0.153
    print cost.T
                
    #MarginalEmissionsData = r2['results'][0]['marginal_carbon']['value']
    #print MarginalEmissionsData
    
def getPyisoData():
    LMPData = CAISO.get_lmp(latest=True)
    df = pd.DataFrame(LMPData)
    #print df    
    #BerkeleyLMPID = df.loc[4900,'node_id']
    #print BerkeleyLMPID
    BerkeleyLMP = df.loc[4900,'lmp']
    print BerkeleyLMP
    #df.to_csv('data.csv', sep='\t')
    #BerkeleyData = df.loc[label]
    #GRIZZLY_7_N101 (Index 4900)

def getFridgeData():
    base = 'http://netfridge-jgilles.c9users.io/' #http://127.0.0.1:5000/' 
    query = {}
    header = {'Content-Type':'application/json'}
    
    endpoint = 'network/Demo/object/Waves/stream/FridgeTemp'
    address = base + endpoint
    query = {'limit':1}
    r = requests.request('get', address, params=query, headers=header, timeout=120 )
    #print r.text
    r2 = json.loads(r.text)
    fridgeTemp = r2['objects']['Waves']['streams']['FridgeTemp']['points'][0]['value']
    #print fridgeTemp
    
    endpoint = 'network/Demo/object/Waves/stream/OutsideTemp'
    address = base + endpoint
    query = {'limit':1}
    r = requests.request('get', address, params=query, headers=header, timeout=120 )
    #print r.text
    r2 = json.loads(r.text)
    outsideTemp = r2['objects']['Waves']['streams']['OutsideTemp']['points'][0]['value']
    #print outsideTemp
    
    endpoint = 'network/Demo/object/Waves/stream/CompressorState'
    address = base + endpoint
    query = {'limit':1}
    r = requests.request('get', address, params=query, headers=header, timeout=120 )
    #print r.text
    r2 = json.loads(r.text)
    compressorState = r2['objects']['Waves']['streams']['CompressorState']['points'][0]['value'] - 10
    #print compressorState
    return (fridgeTemp, outsideTemp, compressorState)
  
def convertWT(WTPacific):
    hrPacific = np.mod(np.add(WTPacific[:,0], 8),24)
    #print hrPacific
    mC = np.zeros((24*12,1))
    for i in range(0,len(hrPacific)):
        for j in range(0,12):
            mC[i*12+j] = WTPacific[i,1]
    #print mC.T
    return (mC,int(hrPacific[0]))
    
#What up my dog

def getCost(currtime):
    #get the cost data
    cost = np.zeros((24*12,1))
    for i in range(currtime, currtime+24):
        for j in range(0, 12):      
            print i
            ti = np.mod(i,24)*12 + j
            if ti < 5*12+30/5 or ti > 16*12+30/5:
                cost[ti] = 0.173
            else:
                cost[ti] = 0.153
    return cost
            
            
def optimize(fridgeTemp, outsideTemp, compressorState, carbon, cost):
    #define parameters

    #Define starting parameters
    f0 = fridgeTemp
    a0 = outsideTemp
    c0 = compressorState
    (f1, a1) = nextTemps(f0,a0,c0)
    C = {'carbon':carbon, 'dollars':cost}
    
    endi = 12
    i = 0
    #Let y be the compressor state
    print f1, a1, c0
    (y, points) = recurse(f1,a1,i,endi,C)
    print "This is the End:", y , points
    return (y, points)

def recurse(f,a,i,endi,C):
    #print f, a,    
    #print i,
    #print endi
    #print C[1][7]
    if i >= endi:
        return (0,0)
    else: 
        #Set up array to put compressor state to
        #try turring on
        (f1, a1) = nextTemps(f,a,1)
        if f1 > 33:
            (yout, cost1) = recurse(f1, a1, i+1, endi, C)
            cost1 = cost1 + getCostPoint(i,1,C)
            y1 = [1]
            y1 = np.append(y1, yout)
        else:
            y1 = 0
            cost1 = 100000
        #try turring it off
        (f2,a2) = nextTemps(f,a,0)
        if f2 < 38:
            (yout, cost2) = recurse(f2, a2, i+1, endi, C)
            cost2 = cost2 + getCostPoint(i,0,C)
            y2 = [0]
            y2 = np.append(y2, yout)
        else:
            y2 = 0
            cost2 = 1000000
        if cost1 < cost2:
            return (y1,cost1)
        else:
            return (y2,cost2)
            
def nextTemps(f,a,y):
    xf = 0.98816669
    xa = 0.05
    xc = -8
    
    f2 = xf*f + xa*a + xc*y
    a2 = a
    return (f2,a2)

#Cost if the compressor is on
def getCostPoint(i,y,C):
    #print C
    carbon = C['carbon']
    dollars = C['dollars']
    #print i
    #print carbon.T
    #print dollars.T
    c = y*(carbon[i] + dollars[i])
    return c
    

def isValid(f):
    #Check to see if the temp is valid
    if f > 33 and f < 80:
        return True
    else:
        return False

def normIt(x):
    maxxx = np.max(x)
    return np.divide(x,maxxx)
    
def plotIt(fridgeTemp, outsideTemp, compressorState, carbon, cost, cnext):
    cnext = np.append(compressorState,cnext)
    plttimes = range(0,len(cnext))
    print plttimes
    plt.clf
    print plttimes
    print cnext
    plt.plot(plttimes,cnext)
    f = np.zeros((len(cnext),1))
    f[0] = fridgeTemp
    (f[1], a2) = nextTemps(f[0], outsideTemp, compressorState)
    for i in range(2,len(cnext)):
        (f[i], a2) = nextTemps(f[i-1], outsideTemp, cnext[i-1])
    plt.plot(plttimes,f)
        
def sendToFridge(c):
    base = 'http://netfridge-jgilles.c9users.io/' #+ '?key=CE186'
    # Set query (i.e. http://url.com/?key=value).
    query = {}
    # Set header.
    header = {'Content-Type':'application/json'}
    
    print "Send:",
    # Generature UNIX timestamps for each data point
    #at = int((datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds())
    at = int(time.time())
    #print at
    q = c + 10
    endpoint = 'network/Demo/object/Waves/stream/CompressorState'
    payload = [ {'value':q,'at':at } ]
    print q
    # Set body (also referred to as data or payload). Body is a JSON string.
    body = json.dumps(payload)
    # Form and send request. Set timeout to 2 minutes. Receive response.
    r = requests.request('post', base + endpoint, data=body, params=query, headers=header, timeout=10 )
    print r
    
# Run continuously forever
# with a delay between calls
def delayed_loop():
    print "Delayed Loop"

def runall():
    print "Getting WattTime Data, please wait..."
    WTPacific = getWTForecast()
    print "Data fetch complete"
    (carbon, currtime) = convertWT(WTPacific)
    print carbon.T
    cost = getCost(currtime)
    print cost.T
    
    carbon = normIt(carbon)
    print carbon.T
    cost = normIt(cost)
    print cost.T
    
    (fridgeTemp, outsideTemp, compressorState) = getFridgeData()
    
    (cnext, points) = optimize(fridgeTemp, outsideTemp, compressorState, carbon, cost)
    print cnext
    
    plotIt(fridgeTemp, outsideTemp, compressorState, carbon, cost, cnext)
    
    #Send to the server
    sendToFridge(cnext[0])
    sendToFridge(cnext[0])
    
def main():
    while True:
        runall()
        time.sleep(5*60)
        
main()



"""
mC = getWattTimeData()
#print mC
cost = getCostData()
#print cost
(fridgeTemp, outsideTemp, compressorState) = getFridgeData()

optimize(fridgeTemp, outsideTemp, compressorState)
print fridgeTemp, outsideTemp, compressorState

print time.gmtime(int(time.time()))
"""