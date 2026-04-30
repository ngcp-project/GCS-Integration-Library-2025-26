from threading import Thread
from datetime import datetime
from RabbitMQ.TelemetryPublisher import TelemetryPublisher
from Enum.ConnectionStatus import ConnectionStatus
from Telemetry.Telemetry import Telemetry

class Vehicle():
    def __init__(self, name:str):
        self.name = name
        self.telemetry_publisher : TelemetryPublisher = TelemetryPublisher(vehicleName= name)
        self.heartbeat = None
        self.num_beats_ack = 0
        self.num_beats_sent = 0
        self.num_command_ack = 0
        self.num_command_sent = 0
        self.last_telemetry_time = None 
        self.status = ConnectionStatus(0)
        self.last_telemetry_ack = None
        self.command_status = "N/A"
        pass

    def determine_connection_status(self):
        # some function to determine connection status with the heartbeats & commands
        #update self.status
        pass


    def publish_telemetry(self, telemetry:Telemetry):
        telemetry.VehicleStatus = self.status.value
        self.telemetry_publisher.publish(telemetry)
        pass

    # all of this can be removed later once we start implementing. 
    # this is for the outlining 
    def increment_num_beats_ack(self):
        self.num_beats_ack += 1
    
    def increment_num_beats_sent(self):
        self.num_beats_sent += 1

    def increment_num_command_ack(self):
        self.num_command_ack += 1
    
    def increment_num_command_sent(self):
        self.num_command_sent += 1

    # timestamp format in miliseconds?
    def set_last_beat_time(self, time:int):
        self.last_beat_time = time