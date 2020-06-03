# MQTT 2 Influx

MQTT2Influx is an exporter in the framework of [EnvoT](https://envot.io) - Environment of Things.
This exporter transfers topics with numbers or booleans from a MQTT broker to an InfluxDB Database.

* Get help to configure the exporter

> python mqtt2influx.py -h

* In Docker the arguments can be passed via environment variables

> docker run --rm -e LOGLEVEL=DEBUG envot/mqtt2influx
