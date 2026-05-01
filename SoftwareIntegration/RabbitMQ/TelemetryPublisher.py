import pika
import json
from Telemetry.Telemetry import Telemetry
#constructor
class TelemetryPublisher:
    def __init__(self, vehicleName:str):
        self.vehicleName = vehicleName
        self.hostName = "localhost"
        self.connection = None
        # initilize rabbitmq server
        self.channel = None
        # this will trigger both queue declarations:
        self.setup_rabbitmq()

    def setup_rabbitmq(self):
        # our rabbitmq server will require user/password 
        credentials = pika.PlainCredentials('admin', 'admin')
        parameters = pika.ConnectionParameters(host = self.hostName, credentials= credentials, virtual_host= "/")
        self.connection =  pika.BlockingConnection(parameters)
        #create a channel
        self.channel = self.connection.channel()
        #create telemetry queue for each vehicle
        self.channel.queue_declare(queue=f"telemetry_{self.vehicleName}", durable = True)
        #create rssi queue for each vehicle
        # self.channel.queue_declare(queue=f"rssi_{self.vehicleName}", durable= True)
    
    def publish(self, data : Telemetry):
        print(data)
        if self.channel == None:
            raise Exception("RabbitMQ channel not initialized")
        try:
            if hasattr(data, 'ToJSON'):
                # Serialize obj to a JSON formatted str.
                message = data.ToJSON()
                message2 = message.encode("utf-8")
            else:
                message2 = message.encode("utf-8")
            self.channel.basic_publish(
                exchange= '',
                routing_key=f"telemetry_{self.vehicleName}",
                body = message2
            )
            print(f"Published telemetry for {self.vehicleName}")
        except Exception as e:
            print(f"Failed to publish telemetry in the queue: {e}")
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
                
                
        