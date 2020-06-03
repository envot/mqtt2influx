#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to export MQTT traffic to Influx DB
# Klemens Schueppert : schueppi@envot.net

import argparse
import time
import signal
import logging 

import paho.mqtt.client as mqttClient
from influxdb import InfluxDBClient 


HOMIE_SET = "set"

parser = argparse.ArgumentParser(description='MQTT2Influx is an exporter from MQTT Broker to InfluxDB. The exporter can be configured via the following arguments:')
parser.add_argument('-MQTThost', type=str, help='Host of MQTT Broker. STR Default: "localhost"')
parser.add_argument('-MQTTport', type=str, help='Port of MQTT Broker. INT Default: 1883')
parser.add_argument('-MQTTname', type=str, help='Connection name at MQTT broker. STR Default: exporter')

parser.add_argument('-DBhost', type=str, help='Host of InfluxDB. STR Default: "localhost"')
parser.add_argument('-DBport', type=str, help='Port of InfluxDB. INT Default: 8086')
parser.add_argument('-DBdatabase', type=str, help='Database of InfluxDB. INT Default: monitoring')
parser.add_argument('-DBuser', type=str, help='User of InfluxDB. INT Default: user')
parser.add_argument('-DBpassword', type=str, help='Password for user of InfluxDB. INT Default: password')

parser.add_argument('-LogLevel', type=str, help='Log leveel. Str Default: INFO')
args = parser.parse_args()

if args.DBhost == None:
    args.DBhost = "localhost"
if args.DBport == None:
    args.DBport = 8086
if args.DBdatabase == None:
    args.DBdatabase = 'monitoring'
if args.DBuser == None:
    args.DBduser = 'user'
if args.DBpassword == None:
    args.DBdpassword = 'password' 

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
            host=args.DBhost,
            port=int(args.DBport),
            username=args.DBuser,
            password=args.DBpassword,
            database=args.DBdatabase,
            timeout = 1)

def sendSingle(deviceName, topic, value):
    json_body = [{ "measurement": str(deviceName), "fields" : {str(topic): float(value)}}]
    logging.debug('Write to InfluxDB: %s'% json_body)
    clientDB.write_points(json_body)


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
    if not (topicNameArray[-1] == HOMIE_SET or
        topicNameArray[-1][0] == '$'):
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
            if topicMessage.lower() in ['on']:
                value = 1
            if topicMessage.lower() in ['off']:
                value = 0
            else:
                return None
                logging.debug('Could not converted message.')
            logging.debug('Converted message to INT: %i'% value)
    return value


def on_message(clientMQTT, userdata, message):
    topicName = message.topic
    topicMessage = message.payload.decode()
    topicNameArray = topicName.split('/')
    logging.debug('Received MQTT message: %s @ %s'% (topicMessage, topicName))
    if not topic_check(topicNameArray):
        return False
    value = convert_message(topicMessage)
    if not value == None:
        deviceName = '/'.join(topicNameArray[:2])
        topic = '/'.join(topicNameArray[2:])
        sendSingle(deviceName, topic, value)


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
