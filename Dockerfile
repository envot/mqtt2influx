FROM python:3.9.12-alpine3.15

MAINTAINER Klemens Schueppert "schueppi@envot.net"

WORKDIR /mqtt2influx/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./mqtt2influx.py /mqtt2influx/

ENV PYTHONUNBUFFERED TRUE

ENV MQTTHOST broker
ENV MQTTPORT 1883
ENV MQTTNAME exporter

ENV DBHOST database
ENV DBPORT 8086
ENV DBORG org
ENV DBBUCKET bucket
ENV DBTOKEN token
ENV LOGLEVEL INFO

ENTRYPOINT python mqtt2influx.py -MQTThost $MQTTHOST -MQTTport $MQTTPORT -MQTTname $MQTTNAME \
            -DBhost $DBHOST -DBport $DBPORT \
            -DBorg $DBORG -DBbucket $DBBUCKET -DBtoken $DBTOKEN \
            -LogLevel $LOGLEVEL
