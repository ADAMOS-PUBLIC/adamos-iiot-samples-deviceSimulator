# -*- coding: utf-8 -*-

import requests, base64, json, logging, os, time, sys, csv
from random import randint
from datetime import datetime
from threading import Thread

logging.basicConfig(level=logging.DEBUG)

logging.info(os.environ)

'''
Start configuration
'''
C8Y_BASE = os.environ.get('C8Y_BASEURL')
C8Y_TENANT = os.environ.get('C8Y_TENANT')
C8Y_USER = os.environ.get('C8Y_USER')
C8Y_PASSWORD = os.environ.get('C8Y_PASSWORD')
C8Y_SIMULATOR_EXTERNAL_ID = 'myRandomSimulator'
'''
End configuration
'''

logging.info(C8Y_BASE)
logging.info(C8Y_TENANT)
logging.info(C8Y_USER)
logging.info(C8Y_PASSWORD)

AUTH = C8Y_TENANT + '/' + C8Y_USER + ':' + C8Y_PASSWORD
C8Y_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Basic ' + base64.b64encode(AUTH.encode('utf-8')).decode("utf-8")
}

def sendMeasurement(measurement):
    response = requests.post(C8Y_BASE + '/measurement/measurements', headers=C8Y_HEADERS, data=json.dumps(measurement))
    return response.json()

def sendAlarm(alarm):
    response = requests.post(C8Y_BASE + '/alarm/alarms', headers=C8Y_HEADERS, data=json.dumps(alarm))
    return response.json()

def acknowledgeAlarm(alarmId):
    alarm = {
        'status': 'ACKNOWLEDGED'
    }
    response = requests.put(C8Y_BASE + '/alarm/alarms/' + str(alarmId), headers=C8Y_HEADERS, data=json.dumps(alarm))
    return response.json()

def clearAlarm(alarmId):
    alarm = {
        'status': 'CLEARED'
    }
    response = requests.put(C8Y_BASE + '/alarm/alarms/' + str(alarmId), headers=C8Y_HEADERS, data=json.dumps(alarm))
    return response.json()

def sendEvent(event):
    response = requests.post(C8Y_BASE + '/event/events', headers=C8Y_HEADERS, data=json.dumps(event))
    return response.json()

def createRandomTempMeasurement(source):
    return {
        'c8y_Temperature': {
            'T': {
                'value': randint(20, 29),
                'unit': '°C'
            }
        },
        'type': 'c8y_Temperature',
        'source': {
            'id': source
        },
        'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    }

def getNextLine(csvfile, reader):
    line = next(reader, None)
    if line is None:
        csvfile.seek(0)
        line = next(reader, None)
    return line

def getNextMeasurement(csvfile, reader, source):
    line = getNextLine(csvfile, reader)
    return {
        'wait': float(line[4]),
        'measurement': {
            line[0]: {
                line[1]: {
                    'value': float(line[2]),
                    'unit': line[3]
                }
            },
            'type': line[0],
            'source': {
                'id': source
            },
            'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }
    }

def getNextAlarm(csvfile, reader, source):
    line = getNextLine(csvfile, reader)
    return {
        'wait': float(line[4]),
        'alarm': {
        	'source': {
            	'id': source
            },
            'type': line[0],
            'text': line[1],
            'severity': line[2],
            'status': line[3],
            'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }
    }

def getNextEvent(csvfile, reader, source):
    line = getNextLine(csvfile, reader)
    return {
        'wait': float(line[2]),
        'event': {
        	'source': {
            	'id': source
            },
            'type': line[0],
            'text': line[1],
            'time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }
    }

# Check if device already created
response = requests.get(C8Y_BASE + '/identity/externalIds/c8y_SimulatorSerial/' + C8Y_SIMULATOR_EXTERNAL_ID, headers=C8Y_HEADERS)

if (response.status_code == 200):
    deviceId = response.json()['managedObject']['id']
else:
    # Create device
    device = {
        'name': 'Docker Simulator Device',
        'c8y_IsDevice': {}
    }
    response = requests.post(C8Y_BASE + '/inventory/managedObjects', headers=C8Y_HEADERS, data=json.dumps(device))
    deviceId = response.json()['id']
    externalId = {
        'type': 'c8y_SimulatorSerial',
        'externalId': C8Y_SIMULATOR_EXTERNAL_ID
    }
    response = requests.post(C8Y_BASE + '/identity/globalIds/' + deviceId + '/externalIds', headers=C8Y_HEADERS, data=json.dumps(externalId))

logging.info('Device ID: ' + deviceId)


def startMeasurements():
    if os.path.isfile('measurements.csv') == False:
        return
    measurementFile=open('measurements.csv','rU')
    measurementReader = csv.reader(measurementFile, delimiter=',')
    while True:
        measurement = getNextMeasurement(measurementFile, measurementReader, deviceId)
        sendMeasurement(measurement['measurement'])
        time.sleep(measurement['wait'])

def startEvents():
    if os.path.isfile('events.csv') == False:
        return
    eventsFile=open('events.csv','rU')
    eventsReader = csv.reader(eventsFile, delimiter=',')
    while True:
        event = getNextEvent(eventsFile, eventsReader, deviceId)
        sendEvent(event['event'])
        time.sleep(event['wait'])

def startAlarms():
    if os.path.isfile('alarms.csv') == False:
        return
    currentActiveAlarms = {}
    alarmsFile=open('alarms.csv','rU')
    alarmsReader = csv.reader(alarmsFile, delimiter=',')
    while True:
        alarm = getNextAlarm(alarmsFile, alarmsReader, deviceId)
        if alarm['alarm']['status'].lower() == 'active':
            alarmResponse = sendAlarm(alarm['alarm'])
            currentActiveAlarms[alarm['alarm']['type']] = alarmResponse['id']
        if alarm['alarm']['status'].lower() == 'acknowledged':
            id = currentActiveAlarms[alarm['alarm']['type']]
            acknowledgeAlarm(id)
        if alarm['alarm']['status'].lower() == 'cleared':
            id = currentActiveAlarms[alarm['alarm']['type']]
            clearAlarm(id)
            currentActiveAlarms.pop(alarm['alarm']['type'], None)
        time.sleep(alarm['wait'])


thread = Thread(target = startMeasurements)
thread.start()

thread = Thread(target = startEvents)
thread.start()

thread = Thread(target = startAlarms)
thread.start()
