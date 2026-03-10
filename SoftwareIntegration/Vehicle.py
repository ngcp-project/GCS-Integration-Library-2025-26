from threading import Thread
from datetime import datetime
from SoftwareIntegration.RabbitMQ.TelemetryPublisher import TelemetryPublisher
from lib.gcs_infrastructure.lib.gcs_packet.Packet.Enum.ConnectionStatus import ConnectionStatus
from lib.gcs_infrastructure.lib.gcs_packet.Packet.Telemetry.Telemetry import Telemetry

class Vehicle():
    def __init__(self, name:str):
        self.name = name
        self.telemetry_publisher = None
        self.heartbeat = None
        self.num_beats_ack = 0
        self.num_beats_sent = 0
        self.num_command_ack = 0
        self.num_command_sent = 0
        self.last_command_sent = None
        self.last_command_time = None
        self.last_telemetry_time = None 
        self.status = ConnectionStatus(0)
        pass

    def determine_connection_status(self):
        # some function to determine connection status with the heartbeats & commands
        #update self.status
        pass


    def publish_telemetry(self, telemetry:Telemetry):
        #append self.status to telemetry before sending
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