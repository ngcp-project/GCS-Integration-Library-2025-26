from Command import *
from Enum import ConnectionStatus
from xbee import XBee
from Infrastructure import GCSXBee
from Infrastructure import *

Command1 = Heartbeat(ConnectionStatus.ConnectionStatus.Connected)
Command2 = EmergencyStop(0)
Command3 = Heartbeat(ConnectionStatus.ConnectionStatus.Unstable)

PORT = "COM4"

#Read gcs-infrastructure documentation to understand the implications of the following function calls
LaunchXBee(PORT)

SendCommand(Command1)
SendCommand(Command2)
SendCommand(Command3)

Telemetry1 = ReceiveTelemetry()
Telemetry2 = ReceiveTelemetry()
Telemetry3 = ReceiveTelemetry()