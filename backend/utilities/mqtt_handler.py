import paho.mqtt.client as mqtt
import json
from flask import current_app
import os

class MQTTHandler:
    def __init__(self, socketio):
        self.socketio = socketio
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
    def connect(self):
        try:
            mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
            mqtt_port = int(os.getenv('MQTT_PORT', 1883))
            
            self.client.connect(mqtt_broker, mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            current_app.logger.error(f"MQTT Connection failed: {str(e)}")
            return False
            
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            current_app.logger.info("Connected to MQTT broker")
            self.client.subscribe("prescriptions/#")
        else:
            current_app.logger.error(f"Failed to connect to MQTT broker: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        current_app.logger.warning("Disconnected from MQTT broker")
        
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.socketio.emit(msg.topic, payload)
            current_app.logger.info(f"Message forwarded: {msg.topic}")
        except Exception as e:
            current_app.logger.error(f"Message processing error: {str(e)}")
            
    def publish(self, topic: str, message: dict):
        if not self.connected:
            current_app.logger.error("Cannot publish: Not connected to broker")
            return False
            
        try:
            result = self.client.publish(
                f"prescriptions/{topic}",
                json.dumps(message)
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            current_app.logger.error(f"Publish error: {str(e)}")
            return False