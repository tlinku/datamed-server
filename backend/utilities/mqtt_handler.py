import paho.mqtt.client as mqtt
import json
import os
from flask import Flask
from datetime import datetime

class MQTTHandler:
    def __init__(self, socketio, app: Flask):
        self.app = app
        self.socketio = socketio
        self.connected = False
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.logger = app.logger
        

    def connect(self):
        try:
            mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
            mqtt_port = int(os.getenv('MQTT_PORT', 1883))
            
            self.client.connect(mqtt_broker, mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"MQTT Connection failed: {str(e)}")
            return False
            
    def on_connect(self, client, userdata, flags, rc):
        with self.app.app_context():
            if rc == 0:
                self.connected = True
                self.logger.info("Connected to MQTT broker")
                self.client.subscribe("prescriptions/#")
            else:
                self.logger.error(f"Failed to connect to MQTT broker: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        with self.app.app_context():
            self.connected = False
            self.logger.warning("Disconnected from MQTT broker")
        
    def on_message(self, client, userdata, msg):
        with self.app.app_context():
            try:
                payload = json.loads(msg.payload.decode())
                self.socketio.emit(msg.topic, payload)
                self.logger.info(f"Message forwarded: {msg.topic}")
            except Exception as e:
                self.logger.error(f"Message processing error: {str(e)}")
            
    def check_expired_prescriptions(self):
        with self.app.app_context():
            try:
                conn = self.app.db_pool.getconn()
                cur = conn.cursor()
                today = datetime.now().date()
                
                cur.execute("""
                    SELECT COUNT(*) FROM prescriptions 
                    WHERE expiry_date < %s
                """, (today,))
                
                expired_count = cur.fetchone()[0]
                
                if expired_count > 0:
                    self.socketio.emit('expired_prescriptions', {
                        'count': expired_count,
                        'timestamp': str(datetime.now())
                    })
                    self.logger.info(f"Found {expired_count} expired prescriptions")
            except Exception as e:
                self.logger.error(f"Error checking expired prescriptions: {str(e)}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    self.app.db_pool.putconn(conn)