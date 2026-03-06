from threading import Thread
from RabbitMQ.Telemetry import TelemetryRabbitMQ
from lib.gcs_infrastructure.lib.gcs_packet.Packet.Enum.ConnectionStatus import ConnectionStatus

class Vehicle():
    def __init__(self, MacAddr:str, TelemetryPublisher:TelemetryRabbitMQ, heartbeat:Thread):
        self.MacAddr = MacAddr
        self.TelemetryPublisher = TelemetryPublisher
        self.heartbeat = heartbeat
        self.num_beats_ack = 0
        self.num_beats_sent = 0
        self.num_command_ack = 0
        self.num_command_sent = 0
        self.last_beat_time = None 
        self.status = ConnectionStatus(0)
        pass

    def determine_connection_status():
        # some function to determine connection status with the heartbeats & commands
        #update self.status
        pass

    def increment_num_beats_ack(self):
        self.num_beats_ack += 1
    
    def increment_num_beats_sent(self):
        self.num_beats_sent += 1

    def increment_num_command_ack(self):
        self.num_command_ack += 1
    
    def increment_num_command_sent(self):
        self.num_command_sent += 1

    def set_last_beat_time(self, time):
        self.last_beat_time = time

    def publish_telemetry(self, data):
        #append self.status to telemetry before sending
        pass