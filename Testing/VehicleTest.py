from Command import *
from Enum import *
from Infrastructure.InfrastructureInterface import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

import json

PORT = "COM3"

PacketLibrary.SetGCSMACAddress("0013A2004283A0EC")

LaunchVehicleXBee(PORT)

Command1 = ReceiveCommand()
Command2 = ReceiveCommand()
Command3 = ReceiveCommand()

print(Command1)
print(Command2)
print(Command3)

try:
    CommandData1 = json.loads(Command1)
    CommandData2 = json.loads(Command2)
    CommandData3 = json.loads(Command3)
                    
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")

Telemetry1 = Telemetry(CommandData1["Command ID"], CommandData1["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry2 = Telemetry(CommandData2["Command ID"], CommandData2["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry3 = Telemetry(CommandData3["Command ID"], CommandData3["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

SendTelemetry(Telemetry1)
SendTelemetry(Telemetry2)
SendTelemetry(Telemetry3)