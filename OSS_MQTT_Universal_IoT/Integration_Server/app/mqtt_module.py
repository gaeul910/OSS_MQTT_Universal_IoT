import paho.mqtt.client as mqtt
import threading
import time

def get_stats_from_clients(mqtt_client):
    responses = []
    
    def stats_callback(topic, message):
        if topic.endswith('/stats'):
            responses.append(message)
    
    # Set up temporary callback
    original_callback = mqtt_client.message_callback
    mqtt_client.message_callback = stats_callback
    
    # Subscribe to stats responses
    mqtt_client.subscribe('+/stats')
    
    # Publish get stats command
    mqtt_client.publish('broadcast', 'get stats')
    
    # Wait for responses
    time.sleep(2)
    
    # Restore original callback
    mqtt_client.on_message = original_callback
    
    return responses

def operate(mqtt_client, device_id, command, topic="broadcast"):
    responses = []
    device_id = str(device_id)

    def command_callback(_client, _userdata, message):
        responses.append(message.payload.decode())

    original_callback = mqtt_client.client.on_message
    mqtt_client.client.on_message = command_callback

    req_command = device_id + " " + command

    mqtt_client.subscribe('+/response')
    mqtt_client.publish(topic, req_command)

    time.sleep(2)

    mqtt_client.client.on_message = original_callback

    return 0 if any(resp == 'OK' for resp in responses) else -1

class MQTTClient:
    def __init__(self, broker_host, broker_port=1883, client_id=None, username=None, password=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = mqtt.Client(client_id=self.client_id)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.subscribed_topics = set()
        self.message_callback = None

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker: {self.broker_host}:{self.broker_port} (rc={rc})")
        # 재연결 시 구독 유지
        for topic in self.subscribed_topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.topic} -> {msg.payload.decode()}")
        if self.message_callback:
            self.message_callback(msg.topic, msg.payload.decode())

    def connect(self):
        self.client.connect(self.broker_host, self.broker_port)
        # 메시지 수신을 위한 루프를 별도 스레드로 실행
        threading.Thread(target=self.client.loop_forever, daemon=True).start()

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, callback=None):
        self.subscribed_topics.add(topic)
        self.client.subscribe(topic)
        if callback:
            self.message_callback = callback

    def disconnect(self):
        self.client.disconnect()