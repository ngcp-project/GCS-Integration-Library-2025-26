from SoftwareIntegration.RabbitMQ.CommandListener import *
from Enum import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Infrastructure import GCSXBee
from Infrastructure import *
from Infrastructure.GCSXBee import *

Command1 = Heartbeat(ConnectionStatus.Connected)
Command2 = EmergencyStop(0)
Command3 = Heartbeat(ConnectionStatus.Unstable)

PORT = "COM4"


#Read gcs-infrastructure documentation to understand the implications of the following function calls

# PacketLibrary.SetVehicleMACAddress(Vehicle.MRA , "0013A200428396C0")
# PacketLibrary.SetVehicleMACAddress(Vehicle.ERU, )

# LaunchXBee(PORT)

# SendCommand(Command1,VehicleName= Vehicle.MRA)
var = Vehicle.MRA
print(var)
# SendCommand(Command2)
# SendCommand(Command3)

Telemetry1 = ReceiveTelemetry()
Telemetry2 = ReceiveTelemetry()
Telemetry3 = ReceiveTelemetry()