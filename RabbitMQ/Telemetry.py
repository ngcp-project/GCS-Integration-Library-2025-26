import pika
import json

#constructor
class TelemetryRabbitMQ:
    def __init__(self, vehicleName:str, hostname: str):
        self.vehicleName = vehicleName
        self.hostName = hostname
        self.connection = None
        # initilize rabbitmq server
        self.channel = None
        # this will trigger both queue declarations:
        self.setup_rabbitmq(hostname)

    def setup_rabbitmq(self,hostname: str):
        # our rabbitmq server will require user/password 
        credentials = pika.PlainCredentials('admin', 'admin')
        parameters = pika.ConnectionParameters(host = hostname, credentials= credentials, virtual_host= "/")
        self.connection =  pika.BlockingConnection(parameters)
        #create a channel
        self.channel = self.connection.channel()
        #create telemetry queue for each vehicle
        self.channel.queue_declare(queue=f"telemetry_{self.vehicleName}", durable = True)
        #create rssi queue for each vehicle
        # self.channel.queue_declare(queue=f"rssi_{self.vehicleName}", durable= True)
    
    def publish(self, data):
        if self.channel == None:
            raise Exception("RabbitMQ channel not initialized")
        try:
            if hasattr(data, 'to_dict'):
                # Serialize obj to a JSON formatted str.
                message = json.dumps(data.to_dict(), indent = 4, default = str)
            else:
                message = json.dumps(data, indent=4)
            self.channel.basic_publish(
                exchange= '',
                routing_key=f"telemetry_{self.vehicleName}",
                body = message
            )
            print(f"Published telemetry for {self.vehicleName.upper()}")
        except Exception as e:
            print(f"Failed to publish telemtry in the queue: {e}")
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
                
                
        