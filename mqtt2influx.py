#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to export MQTT traffic to Influx DB
# Klemens Schueppert : schueppi@envot.net

import argparse
import time
import signal
import logging 

import paho.mqtt.client as mqttClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


HOMIE_SET = "set"

parser = argparse.ArgumentParser(description='MQTT2Influx is an exporter from MQTT Broker to InfluxDB. The exporter can be configured via the following arguments:')
parser.add_argument('-MQTThost', type=str, help='Host of MQTT Broker. STR Default: "localhost"')
parser.add_argument('-MQTTport', type=str, help='Port of MQTT Broker. INT Default: 1883')
parser.add_argument('-MQTTname', type=str, help='Connection name at MQTT broker. STR Default: exporter')

parser.add_argument('-DBhost', type=str, help='Host of InfluxDB. STR Default: "localhost"')
parser.add_argument('-DBport', type=str, help='Port of InfluxDB. INT Default: 8086')
parser.add_argument('-DBorg', type=str, help='Organization of InfluxDB. INT Default: org')
parser.add_argument('-DBbucket', type=str, help='Bucket of InfluxDB. INT Default: bucket')
parser.add_argument('-DBtoken', type=str, help='Token for InfluxDB. INT Default: token')

parser.add_argument('-LogLevel', type=str, help='Log leveel. Str Default: INFO')
args = parser.parse_args()

if args.DBhost == None:
    args.DBhost = "localhost"
if args.DBport == None:
    args.DBport = 8086
if args.DBorg == None:
    args.DBorg = 'org'
if args.DBbucket == None:
    args.DBbucket = 'bucket'
if args.DBtoken == None:
    args.DBtoken = 'token' 

if args.LogLevel== None:
    args.LogLevel = 'INFO' 

levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
logging.basicConfig(level=levels[args.LogLevel.lower()])
logger = logging.getLogger(__name__)
logging.debug('Started MQTT2InfluxDB.')

clientDB = InfluxDBClient(               
            url="http://"+args.DBhost+":"+str(args.DBport),
            token=args.DBtoken,
            org=args.DBorg)

write_api = clientDB.write_api(write_options=SYNCHRONOUS)

def sendSingle(device, name, topic, value):
    p = Point(device).tag("Name", name).field(topic, float(value))
    logging.debug('Write to InfluxDB: %s'% p)
    write_api.write(bucket=args.DBbucket, record=p)


if args.MQTThost == None:
    args.MQTThost = "localhost"
if args.MQTTport == None:
    args.MQTTport = 1883
if args.MQTTname == None:
    args.MQTTname = "exporter"


def on_connect(clientMQTT, userdata, flags, rc):
    if rc == 0:
        logging.info('MQTT2InfluxDB connected to %s:%s.'% (args.MQTThost, str(args.MQTTport)))
        clientMQTT.subscribe('#')
        logging.info('Subscribed to all topics (#).')
    else:
        logging.warning("MQTT Connection failed.")


def on_disconnect(clientMQTT, userdata, rc):
    if rc != 0:
        logging.warning("Unexpected disconnection.")


def topic_check(topicNameArray):
    if topicNameArray[-1] == HOMIE_SET or topicNameArray[-1][0] == '$':
        return True
    return False

def convert_message(topicMessage):
    value=None
    try:
        value = int(topicMessage)
        logging.debug('Converted message to INT: %i'% value)
    except:
        try:
            value = float(topicMessage)
            logging.debug('Converted message to FLOAT: %f'% value)
        except:
            if topicMessage.lower() in ['on', 'true']:
                value = 1
            elif topicMessage.lower() in ['off', 'false']:
                value = 0
            else:
                logging.debug('Could not converted message.')
                return None
            logging.debug('Converted message to INT: %i'% value)
    return value


def on_message(clientMQTT, userdata, message):
    topicName = message.topic
    topicMessage = message.payload.decode()
    topicNameArray = topicName.split('/')
    logging.debug('Received MQTT message: %s @ %s'% (topicMessage, topicName))
    if topic_check(topicNameArray):
        return False
    value = convert_message(topicMessage)
    if not value == None:
        device = topicNameArray[0]
        name = topicNameArray[1]
        topic = '/'.join(topicNameArray[2:])
        sendSingle(device, name, topic, value)


logging.debug('Connecting to MQTT Broker to %s:%s...'% (args.MQTThost, str(args.MQTTport)))
clientMQTT = mqttClient.Client(args.MQTTname)
clientMQTT.on_connect = on_connect
clientMQTT.on_disconnect = on_disconnect
clientMQTT.on_message = on_message
clientMQTT.connect(args.MQTThost, int(args.MQTTport))
clientMQTT.loop_start()


class Runner:
  run = True
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit)
    signal.signal(signal.SIGTERM, self.exit)

  def exit(self,signum, frame):
    self.run = False

if __name__ == '__main__':
  runner = Runner()
  while runner.run:
    time.sleep(1)
logging.info("Exiting.")
