import threading
import time
import random
import sys
import os

#Added init file to make it a package and change the folder name from xbee-python to xbee_python
#Because it parses better

# importing a module from Xbee 
from xbee_python.src.xbee.XBee import XBee
# importing frame x81 Xbee
from xbee_python.src.xbee.frames.x81 import x81
# importing Telemetry from infra
from gcs_infrastructure.Packet.Telemetry.Telemetry import Telemetry
# importing Emergency stop from infra
from gcs_infrastructure.Packet.Command.EmergencyStop import EmergencyStop
# importing Logger from
from gcs_infrastructure.Logger.Logger import Logger
#RabbitMQ Telemetry
from RabbitMQ.Telemetry import TelemetryRabbitMQ
#RabbitMQ Commands
from RabbitMQ.Command import CommandRabbitMQ

TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03
TAG_PING = 0x04




COMMAND_REGISTRY = {
    1: EmergencyStop,
    "emergency_stop": EmergencyStop
    # Add more like 1: KeepInZone, etc.
}

VEHICLES = {    
    "ALL": {"MAC": "000000000000FFFF", "short": "0000"},
    "MRA": {"MAC": "0013A200424353F7", "short": "0002"},
    "ERU": {"MAC": "0013A20042435EA9", "short": "0003"},
    # "ERU": {"MAC": "0013A20042435A3D", "short": "0005"},
    # "MEA": {"MAC": "0013A2004243672F", "short": "0004"}
}
VEHICLE_STATUS = {
    0 : "In Use",
    1 : "Standby",
    2 : "Emergency Stoped",
}

logger = Logger(log_to_console=True)
# this is for the Xbee which we dont have it right now
# gcs_xbee = XBee(port =PORT, baudrate= 115200, loggger = logger)
# gcs_xbee.open()

terminate_event = threading.Event()
telemetry_publisher = {}

# for each vehicle we are gonna create a new publisher
def get_or_create_publisher(vehicle_name:str):
    if vehicle_name not in telemetry_publisher:
        telemetry_publisher[vehicle_name] = TelemetryRabbitMQ(vehicleName= vehicle_name.lower(), hostname= 'localhost')
    return telemetry_publisher[vehicle_name]

def testing():
    while True:
        vehicles =["ERU", "MRA", "FRA", "MEA"]
        for vehicle in vehicles:
            telemetry =  Telemetry(
                speed = round(random.uniform(0.0, 30.0), 2),
                pitch = round(random.uniform(-180.0, 180.0),2),
                yaw = round(random.uniform(-123.0, 123.0), 2),
                roll = round(random.uniform(-123.0, 123.0),2 ),
                altitude= round(random.uniform(0.0, 500.0),2),
                battery_life= random.randint(-100,40),
                last_updated= time.time(),
                current_latitude= round(33.123 + random.uniform(-0.01, 0.01),2),
                current_longitude= round(-123.233 + random.uniform(-0.01, 0.01), 2),
                vehicle_status= random.randint(0,2),
                message_flag= random.randint(0,2),
                message_lat= round(random.uniform(-90.0, 90.0),6),
                message_lon = round(random.uniform(-180.0, 180.0),6),
                patient_status= random.randint(0,2)
            )
            encoded_data = telemetry.encode()
            logger.write(f"Encoded to {len(encoded_data)} bytes")
            decoded_telemetry = telemetry.decode(encoded_data)
            telemetry_dict = {
               "vehicle_id": vehicle.lower(),
                "signal_strength": random.randint(-100 , 40 ),
                "pitch": decoded_telemetry.pitch,
                "yaw": decoded_telemetry.yaw,
                "roll": decoded_telemetry.roll,
                "speed":  decoded_telemetry.speed,
                "altitude":  decoded_telemetry.altitude,
                "battery_life": decoded_telemetry.battery_life,
                "current_position": {
                    "latitude":  decoded_telemetry.current_latitude,
                    "longitude":  decoded_telemetry.current_longitude,
                },
                "vehicle_status": VEHICLE_STATUS[decoded_telemetry.vehicle_status],
                "request_coordinate":{
                    "message_flag": decoded_telemetry.message_flag,
                    "request_location":{
                        "latitude":decoded_telemetry.message_lat,
                        "longitude":decoded_telemetry.message_lon,
                     }
                },
                "patient_secured":decoded_telemetry.patient_status,
                            }
            
            publisher = get_or_create_publisher(vehicle.lower())
            publisher.publish(telemetry_dict)
            logger.write(f"test telemetry data for {vehicle}: {telemetry_dict}")
            # logger.write(telemetry_dict)
            time.sleep(1)


def parse_and_export_telemetry(telemetry: Telemetry, vehicle_name: str, rssi: int):
    telemetry_dict = {
        "vehicle_id": vehicle_name.lower(),
        "signal_strength": rssi,
        "pitch": telemetry.pitch,
        "yaw": telemetry.yaw,
        "roll": telemetry.roll,
        "speed": telemetry.speed,
        "altitude": telemetry.altitude,
        "battery_life": int(telemetry.battery_life),
        "current_position": {
            "latitude": telemetry.current_latitude,
            "longitude": telemetry.current_longitude,
        },
        # "lastUpdated": telemetry.last_updated,
        "vehicle_status": VEHICLE_STATUS[telemetry.vehicle_status],
        "request_coordinate": {
            "message_flag": 0,
            "request_location": {
                "latitude": telemetry.message_lat,
                "longitude": telemetry.message_lon,
            }
        },
        "patient_secured": telemetry.patient_status,
    }
    try:
        publisher = get_or_create_publisher(vehicle_name)
        publisher.publish(telemetry_dict)
        # export_rssi(vehicle_name, rssi)
        logger.write(f"Published telemetry for {vehicle_name}")
    except Exception as e:
        import traceback
        logger.write(f"[!] Failed to publish telemetry for {vehicle_name}: {e}")
        logger.write(traceback.format_exc())

def handle_ui_command(msg: dict):
    """
    Handles a UI-issued command received from RabbitMQ.
    Expects: { "vehicle_name": str, "command_id": int, "value": ... }
    """
    logger.write(f"Message: {msg}")
    vehicle = msg.get("vehicle_id")
    print(vehicle)
    command_id = msg.get("commandID")
    print(command_id)
    value = msg.get("coordinates")
    print(value)

    if vehicle not in VEHICLES:
        logger.write(f"[!] Unknown vehicle: {vehicle}")
        return

    if command_id not in COMMAND_REGISTRY:
        logger.write(f"[!] Unknown command_id: {command_id}")
        return

    command_cls = COMMAND_REGISTRY[command_id]
    command_packet = command_cls.encode_packet((0))
    # # Send command over XBee
    # gcs_xbee.transmit_data(command_packet, address=VEHICLES[vehicle]["MAC"])
    logger.write(f"Sent command {command_id} to {vehicle} with value {value}")

def close_connection():
    terminate_event.set()
    # gcs_xbee.close()
    
    for connection in telemetry_publisher.values():
        if connection != None:
            connection.close_connection()
    logger.write("GCS shutdown complete.")
    

def listen_for_telemetry():
    flag = 0
    while not terminate_event.is_set():
        try:
            frame: x81 = gcs_xbee.retrieve_data()
            if not frame:
                time.sleep(0.05)
                continue

            src_16bit = frame.source_address.hex().upper().zfill(4)
            vehicle_name = next((name for name, info in VEHICLES.items() if info["short"] == src_16bit), "UNKNOWN")
            # logger.write(f"Frame Data: {frame.data}")
            # logger.write(Telemetry.decode(frame.data))

            if isinstance(frame.data, Telemetry):
                telemetry = frame.data 
            elif isinstance(frame.data, bytes) and frame.data[0] == TAG_TELEMETRY:
                try:
                    telemetry = Telemetry.decode(frame.data)
                except Exception as e:
                    logger.write(f"[!] Failed to decode raw telemetry: {e}")
                    continue
            else:
                if isinstance(frame.data, bytes) and frame.data[0] == TAG_ACK:
                    logger.write(f" Received ACK from {vehicle_name}: {frame.data[1:].decode(errors='ignore')}")
                else:
                    logger.write(f"[!] Unknown data from {vehicle_name}")
                continue

            logger.write(f"Telemetry from {vehicle_name} (RSSI: {frame.rssi})")
            logger.write(f"Telemetry Data: {telemetry}")
            parse_and_export_telemetry(telemetry, vehicle_name, frame.rssi)

            # Send ping back
            ping_payload = bytes([TAG_PING])
            mac = VEHICLES.get(vehicle_name, {}).get("MAC")
            if mac and mac != "NaN":
                try:
                    gcs_xbee.transmit_data(ping_payload, address=mac)
                    logger.write(f"Sent PING to {vehicle_name}")
                except Exception as e:
                    logger.write(f"[!] Error sending PING: {e}")

        except Exception as e:
            logger.write(f"[!] Error in listen_for_telemetry: {e}")
            time.sleep(0.2)

    

def main():
    # command_test_thread = threading.Thread(target=command_test, daemon=True)
    #telemetry_thread = threading.Thread(target=listen_for_telemetry, daemon=True)
    telemetry_testing = threading.Thread(target= testing, daemon = True)
    telemetry_testing.start()
    
    # Start RabbitMQ Command Consumer
    consumer = CommandRabbitMQ(
        on_command=handle_ui_command
    )
    
    #Declare
    consumer_thread = threading.Thread(target=consumer.start, daemon=True)
    consumer_thread.start()
    
    
    # command_test_thread.start()
    #telemetry_thread.start()

    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        logger.write("\n Shutdown requested by user.")
    finally:
        # consumer.stop()
        close_connection()


if __name__ == "__main__":
    main()












