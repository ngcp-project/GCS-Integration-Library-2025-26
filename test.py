from Command import *
from Enum import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Infrastructure import *

Command1 = Heartbeat(ConnectionStatus.Connected)
Command2 = EmergencyStop(0)
Command3 = Heartbeat(ConnectionStatus.Unstable)

PORT = "COM4"

#Read gcs-infrastructure documentation to understand the implications of the following function calls

PacketLibrary.SetVehicleMACAddress(Vehicle.MRA, "0013A200428396C0")

LaunchXBee(PORT)

SendCommand(Command1, Vehicle.MRA)
SendCommand(Command2, Vehicle.MRA)
SendCommand(Command3, Vehicle.MRA)

Telemetry1 = ReceiveTelemetry()
Telemetry2 = ReceiveTelemetry()
Telemetry3 = ReceiveTelemetry()

print(Telemetry1)
print(Telemetry2)
print(Telemetry3)