#!/bin/bash

case "$1" in
  "start")
    if pgrep mosquitto > /dev/null; then
      echo "Mosquitto is already running"
    else
      echo "Starting Mosquitto MQTT broker..."
      mosquitto -d
      echo "Mosquitto started"
    fi
    ;;
  "stop")
    if pgrep mosquitto > /dev/null; then
      echo "Stopping Mosquitto MQTT broker..."
      pkill mosquitto
      echo "Mosquitto stopped"
    else
      echo "Mosquitto is not running"
    fi
    ;;
  *)
    echo "Usage: ./mqtt.sh {start|stop}"
    ;;
esac
