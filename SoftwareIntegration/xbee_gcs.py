# This is the main manager for all of Software Integration's duties.
from datetime import datetime
import threading
import time
from VehicleObj import VehicleObj
from RabbitMQ import TelemetryPublisher, CommandListener
from Acknowledgement import Acknowledgement
from Command import EmergencyStop, Heartbeat, PatientLocation, AddZone
from Telemetry.Telemetry import Telemetry
from RabbitMQ.CommandListener import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Infrastructure import GCSXBee
from Infrastructure import *
from Enum import Vehicle, ConnectionStatus, ZoneType
# /Users/puma/GCS-Integration-Library-2025-26/gcs-packet/Packet/Enum/Vehicle.py

VEHICLES = {
    # "Vehicle Name" : "Vehicle object" 
}

ACK_MAP = {
    # packet_id : "Acknowledgement object" 
    3 :  Acknowledgement(command_id= 2, vehicle_id= Vehicle.MRA, time= 4.23)
}

ZONE_TYPE_COORDINATES_MAP = {
    3 : {"zoneType": ZoneType.KeepIn,"coordinates":[]},
    4 : {"zoneType": ZoneType.KeepOut,"coordinates":[]},
    5 : {"zoneType": ZoneType.SearchArea,"coordinates":[]},
}

VEHICLE_ENUM = {
    "ERU" :  Vehicle.ERU,
    "MRA" :  Vehicle.MRA,
    "MEA" :  Vehicle.MEA,
    "ALL" : Vehicle.ALL
}

COMMAND_IDS = [i for i in range(1, 5)]

#create a lock for sending commands & heartbeat threads. Only one can be done at a time
#global lock
command_lock = threading.Lock()

#event for graceful shutdown of program
shutdown = threading.Event()

consumer = CommandListener()
# 1 thread for telemetry manager
def telemetry_manager() -> None:
    print(f"Telemetry Manager Started")
    while not shutdown.is_set():
        # print(ACK_MAP)
        # check telemetry for command ack
        # use an enum for knowing which vehicle it is 
        telemetry_instance = ReceiveTelemetry() 
        if not telemetry_instance:
            continue
        
        packet_id = telemetry_instance.PacketID
        vehicle_id = telemetry_instance.Vehicle
        command_id = telemetry_instance.CommandID
        vehicle_instance = VEHICLES[vehicle_id]

        ack_status = check_ack_status(vehicle_id=vehicle_id,
                                      packet_id=packet_id, 
                                      command_id=command_id, 
                                      time_arrived=time.time())
        
        if ack_status:
            send_command_ack(vehicle_id=vehicle_id, command_id= command_id)
            if command_id == Heartbeat.COMMAND_ID:
                vehicle_instance.increment_num_command_ack()
            else:
                vehicle_instance.increment_num_beats_ack()
        
        vehicle_instance.publish_telemetry(telemetry_instance)

    print(f"Telemetry Manager Shutting Down")

# Each vehicle will need a heartbeat manager
def heartbeat_manager(vehicle: VehicleObj) -> None:
    prevStatus = vehicle.status
    counter = 0
    # sends the heartbeat once every second
    while not shutdown.is_set():
        vehicle.determine_connection_status()

        # stop reconnection attempts after 10 failed attempts
        if counter == 10:
            break

        # 10 reconnection attempts if it is disconnected 10 times in a row
        if vehicle.last_telemetry_packet and prevStatus == ConnectionStatus.Disconnected:
            counter+=1
            vehicle.publish_telemetry(vehicle.last_telemetry_packet)
        prevStatus = vehicle.status

        # Send the command
        with command_lock:
            print(f"Heartbeat for {vehicle.id} with status {vehicle.status}")
            send_command(command_id=Heartbeat.COMMAND_ID, vehicle_id= vehicle.id, args=vehicle.status)
            vehicle.increment_num_beats_sent()
        
        time.sleep(Acknowledgement.WAITTIMEINSECONDS)
    
    print(f"{vehicle.id} sent {vehicle.num_beats_sent} beats")
    print(f"Heartbeat for {vehicle.id} Shutting Down")

# 1 thread for commands
# def command_manager(command_listener: CommandListener) -> None:
def command_manager(message : dict) -> None:
    vehicle_id = message.get("vehicle_id")
    command_id = message.get("command_id")
    coordinates = message.get("coordinates")
    vehicle_id_enum =  VEHICLE_ENUM[vehicle_id]
    print(vehicle_id)
    print(command_id)
    if command_id in ZONE_TYPE_COORDINATES_MAP and coordinates:
            list_of_coordinates = []
            for coordinate in coordinates:
                list_of_coordinates.append((coordinate.get('lat'), coordinate.get('long')))
            zone_type_coordinate_instance = ZONE_TYPE_COORDINATES_MAP.get(command_id)
            zone_type_coordinate_instance["coordinates"] =  list_of_coordinates
            with command_lock:
                send_command(command_id= AddZone.COMMAND_ID, vehicle_id=vehicle_id_enum, args=zone_type_coordinate_instance)
    else:
        with command_lock:
            send_command(command_id,  vehicle_id_enum , args= None)
    
        # might refactor the check_ack_status 
    print(f"Command Manager Shutting Down")

def check_ack_status(vehicle_id: Vehicle, packet_id : int, command_id: int, time_arrived : float, debug=False) -> bool:
    # expected_ack = ACK_MAP[packet_id]
    # last_updated should be a float bc it is datetime.datetime()? and it's already in seconds
    # compare to expected_time in expected_ack with time_arrived and command_id
    # return True or False

    if debug:
        if packet_id not in ACK_MAP:
            print(f"packet_id: {packet_id} not found in Ack Map")
            return False
        
        if vehicle_id not in VEHICLES.keys():
            print(f"vehicle_id: {vehicle_id} not found in Vehicles")
            return False
        
        if command_id not in COMMAND_IDS:
            print(f"command_id: {command_id} not found in command ids")
            return False
        
        expected_ack =  ACK_MAP.pop(packet_id)
        
        if expected_ack.command_id != command_id:
            print(f"expected: {expected_ack.command_id} but got {command_id}")
            return False
        if expected_ack.vehicle_id != vehicle_id:
            print(f"expected: {expected_ack.vehicle_id} but got {vehicle_id}")
            return False
        if expected_ack.time < time_arrived:
            print(f"ack exceeded alloted wait time of {Acknowledgement.WAITTIMEINSECONDS}")
            return False
        
        return True
    else: 
        expected_ack =  ACK_MAP.pop(packet_id, None)

        return (expected_ack and 
            vehicle_id in VEHICLES.keys() and 
            command_id in COMMAND_IDS and
            expected_ack.command_id == command_id and 
            expected_ack.vehicle_id == vehicle_id and 
            expected_ack.time < time.time())

def send_command_ack(vehicle_id : Vehicle, command_id : int) -> None:
    #Trigger 
    consumer.resolve_ack(vehicle_id= vehicle_id.name, command_id= command_id)
    pass

# args : parameters for the commands
# for KeepIn, KeepOut, and SearchArea, the args should be 
# args.zone = ZoneType (an enum)
# args.coords = list of coords for the zone\
def send_command(command_id:int, vehicle_id: Vehicle, args = None):
    command_interface = None

    match command_id:
        case Heartbeat.COMMAND_ID:
            command_interface = Heartbeat(args)
        case EmergencyStop.COMMAND_ID:
            command_interface = EmergencyStop(1)
        case AddZone.COMMAND_ID:
            command_interface = AddZone(args["zoneType"], args["coordinates"])
        case PatientLocation.COMMAND_ID:
            command_interface = PatientLocation(args)
    
    if not command_id:
        print(f"Unknown Command: {command_id}" )
        return
        
    if vehicle_id == Vehicle.ALL:
        for vehicle in VEHICLES.values():
            vehicle.increment_num_command_sent()
            packet_id = command_interface.PacketID
            ACK_MAP[packet_id] = Acknowledgement(command_id= command_id, vehicle_id= vehicle_id ,time= time.time())
    else:
        vehicle_instance : VehicleObj= VEHICLES.get(vehicle_id)
        vehicle_instance.increment_num_command_sent()
        # VEHICLES[vehicle_id].increment_num_command_sent()
        packet_id = command_interface.PacketID
        ACK_MAP[packet_id] = Acknowledgement(command_id= command_id, vehicle_id= vehicle_id, time= time.time())

    #Infra function to send to the queue
    SendCommand(command_interface, vehicle_id)

def end_program(command_manager_thread:threading.Thread, telemetry_manager_thread:threading.Thread):
    shutdown.set()
    command_manager_thread.join()
    telemetry_manager_thread.join()
    for vehicle in VEHICLES.values():
        # vehicle.telemetry_publisher.close_connection()
        vehicle.heartbeat.join()
    
    print("Shutdown complete.")
    pass

# we also need a function to clean up the dict/remove acknwoledged commands

def main():
    # List of vehicless
    vehicle_list = [Vehicle.ERU, Vehicle.MRA, Vehicle.MEA]

    #initialize all vehicle objects
    for vehicle_enum in vehicle_list:
        vehicle = VehicleObj(vehicle_id=vehicle_enum)
        # vehicle.telemetry_publisher = TelemetryPublisher(vehicleName=vehicle.name, hostname='localhost'),
        vehicle.heartbeat=threading.Thread(target=heartbeat_manager, args=[vehicle])
        # putting in the map vehicle name and Vehicle class
        VEHICLES[vehicle.id] = vehicle
        print(VEHICLES)

    # 3 threads heartbeat + 1 thread command_manager + 1 thread telemetry manager
    # command_manager_thread = threading.Thread(target=command_manager, args=CommandListener())
    # Declare consumer, declare which function they are gonna use whenever they receive a message
    consumer = CommandListener(
        on_command= command_manager
    )
    # Initialize consumer listener, on_command = handle_ui_command 
    # Declare command_manager thread, actually starting consuming
    command_manager_thread = threading.Thread(target=consumer.start, daemon=False)

    telemetry_manager_thread = threading.Thread(target=telemetry_manager)
    
    # start threads
    telemetry_manager_thread.start()
    command_manager_thread.start()
    # for vehicle in VEHICLES.values():
    #     # for each vehicle you are gonna start the hearbeat
    #     # maybe change this to once we are receiving telemetry then start thread?
    #     vehicle.heartbeat.start()

    # send_command(command_id= 2 , vehicle_id= Vehicle.MRA, args= None)
    Telemetry1 : Telemetry = Telemetry(2,3, 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
    Telemetry1.Vehicle = Vehicle.ERU
    SendTelemetry(Telemetry1)
    #graceful shutdown
    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("\n Shutdown requested by user.")
    finally:
        end_program(command_manager_thread, None)

if __name__ == "__main__":
    main()
