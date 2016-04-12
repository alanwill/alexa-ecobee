# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import requests
import json

def lambda_handler(event, context):

    # Read Alexa Application IDs from DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('alexa-ecobee')
    response = table.scan()
    applicationIds = list()
    for i in response['Items']['applicationId']:
        applicationIds.append(i)

    applicationId = event['session']['application']['applicationId']
    if applicationId not in applicationIds:
        return ({ "response": { "outputSpeech": { "type": "PlainText", "text": "Sorry, you're not authorized to use this app." }, "shouldEndSession": "true" } })

    if event['request']['type'] == 'IntentRequest':
        return handleIntent(context, event)

    if event['header']['namespace'] == 'Alexa.ConnectedHome.Discovery':
        return handleDiscovery(context, event)

    elif event['header']['namespace'] == 'Alexa.ConnectedHome.Control':
        return handleControl(context, event)

def handleDiscovery(context, event):
    payload = ''
    header = {
        "namespace": "Alexa.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesResponse",
        "payloadVersion": "2"
        }

    if event['header']['name'] == 'DiscoverAppliancesRequest':
        payload = {
            "discoveredAppliances":[
                {
                    "applianceId":"device001",
                    "manufacturerName":"yourManufacturerName",
                    "modelName":"model 01",
                    "version":"your software version number here.",
                    "friendlyName":"Smart Home Virtual Device",
                    "friendlyDescription":"Virtual Device for the Sample Hello World Skill",
                    "isReachable":True,
                    "actions":[
                        "turnOn",
                        "turnOff"
                    ],
                    "additionalApplianceDetails":{
                        "extraDetail1":"optionalDetailForSkillAdapterToReferenceThisDevice",
                        "extraDetail2":"There can be multiple entries",
                        "extraDetail3":"but they should only be used for reference purposes.",
                        "extraDetail4":"This is not a suitable place to maintain current device state"
                    }
                }
            ]
        }

def handleControl(context, event):
    payload = ''
    device_id = event['payload']['appliance']['applianceId']
    message_id = event['header']['messageId']

    if event['header']['name'] == 'TurnOnRequest':
        payload = { }

    header = {
        "namespace":"Alexa.ConnectedHome.Control",
        "name":"TurnOnConfirmation",
        "payloadVersion":"2",
        "messageId": message_id
        }

def handleIntent(context, event):
    payload = ''
    intentName = event['request']['intent']['name']
    slotName = event['request']['intent']['slots']
    accessToken = event['session']['user']['accessToken']

    if intentName == 'GetTemperature':
        thermostatUrl = "https://api.ecobee.com/1/thermostat"
        thermostatQueryString = {
            "json": "{\"selection\":{\"includeAlerts\":\"true\",\"selectionType\":\"registered\",\"selectionMatch\":\"\",\"includeEvents\":\"true\",\"includeSettings\":\"false\",\"includeRuntime\":\"true\"}}"}
        headersrauth = "Bearer " + accessToken

        headers = {'content-type': "application/json;charset=UTF-8", 'cache-control': "no-cache"}
        headers['authorization'] = headersrauth

        thermostatResponse = requests.request("GET", thermostatUrl, headers=headers, params=thermostatQueryString)

        data = json.loads(thermostatResponse.text)

        temps = list()
        for thermostat in data['thermostatList']:
            temps.extend((thermostat['name'], float(thermostat['runtime']['actualTemperature']) / 10))

        if len(temps) == 2:
            tempReading = "The temperature is " + str(temps[1]) + " degrees fahrenheit in " + temps[0]
            payload = {"response": {"outputSpeech": {"type": "PlainText", "text": tempReading}, "shouldEndSession": "true"}}
        elif len(temps) == 4:
            tempReading = "The temperature is " + str(temps[1]) + " degrees " + temps[0] + " and " + str(temps[3]) + " degrees fahrenheit " + temps[2]
            payload = {"response": {"outputSpeech": {"type": "PlainText", "text": tempReading}, "shouldEndSession": "true"}}

    return payload

