#!/bin/bash

case "$1" in
  "start")
    mosquitto -v
    ;;
  "stop")
    pkill mosquitto
    ;;
  *)
    echo "Usage: ./mqtt.sh {start|stop}"
    ;;
esac