from Command import *
from Enum import *
from Infrastructure.InfrastructureInterface import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

PORT = "COM4"

#Read gcs-infrastructure documentation to understand the implications of the following function calls

PacketLibrary.SetVehicleMACAddress(Vehicle.MRA, "0013A200428396C0")

LaunchGCSXBee(PORT)

command1 = Heartbeat(ConnectionStatus.Connected)
command2 = EmergencyStop(0)
command3 = Heartbeat(ConnectionStatus.Disconnected)

SendCommand(command1, Vehicle.MRA)
SendCommand(command2, Vehicle.MRA)
SendCommand(command3, Vehicle.MRA)

telemetry1 = ReceiveTelemetry()
telemetry2 = ReceiveTelemetry()
telemetry3 = ReceiveTelemetry()

print(f"({telemetry1.Vehicle}, {telemetry1.MACAddress})")

print(telemetry1)
print(telemetry2)
print(telemetry3)