FROM python:3.7.7-alpine3.11

MAINTAINER Klemens Schueppert "schueppi@envot.net"

WORKDIR /mqtt2influx/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./mqtt2influx.py /mqtt2influx/

ENV MQTTHOST broker
ENV MQTTPORT 1883
ENV MQTTNAME exporter

ENV DBHOST database
ENV DBPORT 8086
ENV DBDATABASE monitoring
ENV DBUSER user
ENV DBPASSWORD password
ENV LOGLEVEL INFO

ENTRYPOINT python mqtt2influx.py -MQTThost $MQTTHOST -MQTTport $MQTTPORT -MQTTname $MQTTNAME \
            -DBhost $DBHOST -DBport $DBPORT \
            -DBdatabase $DBDATABASE -DBuser $DBUSER -DBpassword $DBPASSWORD \
            -LogLevel $LOGLEVEL
