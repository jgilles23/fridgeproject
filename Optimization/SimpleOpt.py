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
import requests
import json
import numpy as np
#import datetime as dt
from datetime import datetime
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
    compressorState = r2['objects']['Waves']['streams']['CompressorState']['points'][0]['value']
    #print compressorState
    return (fridgeTemp, outsideTemp, compressorState)
    
def optimize(fridgeTemp, outsideTemp, compressorState):
    #define parameters
    xf = 
    
# Run continuously forever
# with a delay between calls
def delayed_loop():
    print "Delayed Loop"


mC = getWattTimeData()
#print mC
cost = getCostData()
#print cost
(fridgeTemp, outsideTemp, compressorState) = getFridgeData()

optimize(fridgeTemp, outsideTemp, compressorState)
print fridgeTemp, outsideTemp, compressorState

print time.gmtime(int(time.time()))