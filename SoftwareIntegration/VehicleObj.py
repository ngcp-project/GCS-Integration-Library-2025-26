from threading import Thread
from time import time
from RabbitMQ.TelemetryPublisher import TelemetryPublisher
from Enum.ConnectionStatus import ConnectionStatus
from Telemetry.Telemetry import Telemetry
from Enum.Vehicle import Vehicle as Vehicle

class VehicleObj():
    CONNECTED_ACK_PERCENT = 0.8
    UNSTABLE_ACK_PERCENT = 0.5
    NAME_FORMAT = {
        Vehicle.ERU : "eru",
        Vehicle.MRA : "mra",
        Vehicle.MEA : "mea"
    }
    def __init__(self, vehicle_id:Vehicle):
        self.id = vehicle_id
        self.telemetry_publisher : TelemetryPublisher = TelemetryPublisher(vehicleName= VehicleObj.NAME_FORMAT[vehicle_id] )
        self.heartbeat = None
        self.num_beats_ack = 0
        self.num_beats_sent = 0
        self.num_command_ack = 0
        self.num_command_sent = 0
        self.last_telemetry_time = None 
        self.status = ConnectionStatus.Connected
        self.last_telemetry_ack = None
        self.last_telemetry_packet = None
        self.command_status = "N/A"
        pass

    def determine_connection_status(self):
        if self.last_telemetry_time == None:
            self.status = ConnectionStatus.Disconnected
            return
        time_since = time.time() - self.last_telemetry_time
        percent_ack = self.num_beats_ack/(self.num_beats_sent-1) if time_since < 1 else self.num_beats_ack/self.num_beats_sent
        if percent_ack >= Vehicle.CONNECTED_ACK_PERCENT:
            self.status = ConnectionStatus.Connected
        elif percent_ack >= Vehicle.UNSTABLE_ACK_PERCENT:
            self.status = ConnectionStatus.Unstable
        else:
            self.status = ConnectionStatus.Disconnected


    def publish_telemetry(self, telemetry:Telemetry):
        telemetry.VehicleStatus = self.status.name
        self.last_telemetry_packet = telemetry
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
    def set_last_beat_time(self, time:float):
        self.last_beat_time = time