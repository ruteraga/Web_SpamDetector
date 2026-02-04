import paho.mqtt.client as mqtt
import json
import time
from typing import Callable
import requests

class MQTTSpamClient:
    def __init__(self, broker="localhost", port=1883, api_url="http://api:8000"):
        self.broker=broker
        self.port=port
        self.api_url=api_url
        self.client=mqtt.Client()
        self.client.on_connect=self.on_connect
        self.client.on_message=self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code {rc}")

        client.subscribe("messages/incoming")
        client.subscribe("messages/batch")

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}")

        try:
            payload=json.load(msg.payload.decode())

            if msg.topic == "messages/incoming":
                self.process_single_message(payload)
            elif msg.topic == "messages/batch":
                self.process_batch_messages(payload)

        except Exception as e:
            print(f"Error processing message: {e}")
            client.publish("messages/error", json.dumps({"error":str(e)}))

    def process_single_message(self, payload):

        try:

            response=requests.post(
                f"{self.api_url}/predict",
                json={"text": payload.get("text", ""), "user_id": payload.get("user_id")}
            )

            if response.status_code == 200:
                result=response.json()

                self.client.publish(
                    "messages/classified",
                    json.dumps({
                        **payload,
                        **result,
                        "timestamp":time.time()
                    })
                )

                if result["is_spam"]:
                    self.client.publish("messages/spam", json.dumps(payload))
                else:
                    self.client.publish("messages/ham", json.dumps(payload))
                
        except Exception as e:
            print(f"API call failed:{e}")
        

    def process_batch_messages(self, payload):
        messages=payload.get("messages", [])

        try:
            response=requests.post(
                f"{self.api_url}/batch_predict",
                json=messages
            )

            if response.status_code == 200:
                results=response.json()
                self.client.publish(
                    "messages/batch_results",
                    json.dumps(results)
                )
        except Exception as e:
            print(f"Batch API call failed: {e}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        print(f"Connecting to MQTT broker at {self.broker}:{self.port}")
        self.client.loop_forever()


if __name__=="__main__":
    client= MQTTSpamClient()
    client.start()
