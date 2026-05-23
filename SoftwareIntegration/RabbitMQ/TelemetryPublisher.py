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
                message = self.to_actual_JSON(data)
                message2 = message.encode("utf-8")
            else:
                message = self.to_actual_JSON(data)
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

    
    def to_actual_JSON(self, data: Telemetry) -> str:
        JSONData = {
            "vehicle_id": str(data.Vehicle.name).lower(),
            "signal_strength": 0,
            "pitch": float(data.Pitch),
            "yaw": float(data.Yaw),
            "roll": float(data.Roll),
            "speed": float(data.Speed),
            "altitude": float(data.Altitude),
            "battery_life": int(data.BatteryLife),
            "current_position": {
                "latitude": float(data.CurrentPositionX),
                "longitude": float(data.CurrentPositionY)
            },
            "vehicle_status": str(data.VehicleStatus),
            "request_coordinate": {
                "message_flag": int(data.MessageFlag),
                "request_location": {
                    "latitude": float(data.MessageLat),
                    "longitude": float(data.MessageLon)
                },
               "patient_secured": bool(data.PatientStatus)
            }
        }

        return json.dumps(JSONData)
                    
                
        