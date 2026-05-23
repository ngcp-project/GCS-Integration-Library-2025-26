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
from Command.CommandInterface import CommandInterface
# /Users/puma/GCS-Integration-Library-2025-26/gcs-packet/Packet/Enum/Vehicle.py

VEHICLES = {
    # "Vehicle Name" : "Vehicle object" 
}

ACK_MAP = {
    # packet_id : "Acknowledgement object" 
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
    "ALL" :  Vehicle.ALL
}

COMMAND_IDS = [i for i in range(1, 5)]

patient_is_found = False
patient_location_manager = None
pending_patient_loc_ids = set() # Set of remaining vehicles to send patient location to

#create a lock for sending commands & heartbeat threads. Only one can be done at a time
#global lock
command_lock = threading.Lock()

#event for graceful shutdown of program
shutdown = threading.Event()

consumer = CommandListener()
# 1 thread for telemetry manager
def telemetry_manager() -> None:
    global patient_is_found, patient_location_manager, pending_patient_loc_ids
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
        message_flag = telemetry_instance.MessageFlag
        
        if not patient_is_found and message_flag == 2:  # message_flag == 2 is Patient
            patient_is_found = True
            patient_location_manager = threading.Thread(target=send_patient_location, args=[telemetry_instance.MessageLat, telemetry_instance.MessageLon])
            patient_location_manager.start()            

        ack_status = check_ack_status(vehicle_id=vehicle_id,
                                      packet_id=packet_id, 
                                      command_id=command_id, 
                                      time_arrived=time.time())
        
        if ack_status:
            print("SEND_COMMAND_ACK")
            if command_id == EmergencyStop.COMMAND_ID or command_id == AddZone.COMMAND_ID:
                # only send_ack for the commands that come from the GCS-Desktop
                send_command_ack(vehicle_id=vehicle_id, command_id= command_id)
            if command_id == Heartbeat.COMMAND_ID:
                vehicle_instance.increment_num_beats_ack()
            elif command_id == PatientLocation.COMMAND_ID:
                print(f"Vehicle {vehicle_id} has acknowledged patient location")
                pending_patient_loc_ids.discard(vehicle_id)
            else:
                vehicle_instance.increment_num_command_ack()
        
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
    
def send_patient_location(lat: float, lon: float):
    coordinates = (lat, lon)
    global pending_patient_loc_ids
    pending_patient_loc_ids.update([vehicle.id for vehicle in VEHICLES.values()])
    
    # Only sends PatientLocation command without acknowledgement at most 10 times
    vehicle_counters = {vehicle_id: 0 for vehicle_id in pending_patient_loc_ids}
    MAX_COUNT = 10
    COOLDOWN = Acknowledgement.WAITTIMEINSECONDS
    
    while not shutdown.is_set() and pending_patient_loc_ids:
        for vehicle_id in list(pending_patient_loc_ids):
            print(f"Sending patient location to vehicle_id: {vehicle_id}")
            with command_lock:
                send_command(PatientLocation.COMMAND_ID, vehicle_id, args=coordinates)
                
            vehicle_counters[vehicle_id] += 1
            if vehicle_counters[vehicle_id] >= MAX_COUNT:
                print(f"vehicle_id: {vehicle_id} has reached max PatientLocation retries of {MAX_COUNT}")
                pending_patient_loc_ids.discard(vehicle_id)
        
        time.sleep(COOLDOWN)
    

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
        print(expected_ack)

        return (expected_ack and 
            vehicle_id in VEHICLES.keys() and 
            command_id in COMMAND_IDS and
            expected_ack.command_id == command_id and 
            expected_ack.vehicle_id == vehicle_id and 
            abs(expected_ack.time - time.time()) < Acknowledgement.WAITTIMEINSECONDS)

def send_command_ack(vehicle_id : Vehicle, command_id : int) -> None:
    #Trigger
    print(f"vehicle_name= {vehicle_id.name}, command_id ={command_id}" ) 
    consumer.resolve_ack(vehicle_id= vehicle_id.name, command_id= command_id)
    

# args : parameters for the commands
# for KeepIn, KeepOut, and SearchArea, the args should be 
# args.zone = ZoneType (an enum)
# args.coords = list of coords for the zone\
def send_command(command_id:int, vehicle_id: Vehicle, args = None):
    # if vehicle_id == Vehicle.ALL:
    #     for vehicle in VEHICLES.keys():
    #         command_interface = create_new_command(command_id= command_id, args=args)
    #         vehicle_object = VEHICLES[vehicle]
    #         vehicle_object.increment_num_command_sent()
    #         packet_id = command_interface.PacketID
    #         print(packet_id)
    #         ACK_MAP[packet_id] = Acknowledgement(command_id= command_id, vehicle_id= vehicle ,time= time.time())
    #         print(f"This is a map {ACK_MAP}")
            
    # else:
        vehicle_instance : VehicleObj= VEHICLES.get(vehicle_id)
        vehicle_instance.increment_num_command_sent()
        command_interface = create_new_command(command_id= command_id, args = args)
        packet_id = command_interface.PacketID
        ACK_MAP[packet_id] = Acknowledgement(command_id= command_id, vehicle_id= vehicle_id, time= time.time())
        print(ACK_MAP)

        #Infra function to send to the queue
        SendCommand(command_interface, vehicle_id)

def create_new_command(command_id:int, args = None) -> CommandInterface | None:

    available_commands = [Heartbeat.COMMAND_ID, EmergencyStop.COMMAND_ID, AddZone.COMMAND_ID,PatientLocation.COMMAND_ID]
    if command_id not in available_commands:
        print(f"Unknown command {command_id}")
        return None
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

    return command_interface 

def end_program(command_manager_thread:threading.Thread, telemetry_manager_thread:threading.Thread):
    shutdown.set()
    command_manager_thread.join()
    telemetry_manager_thread.join()
    if patient_location_manager:
        patient_location_manager.join()
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
    global consumer
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
    for vehicle in VEHICLES.values():
        # for each vehicle you are gonna start the hearbeat
        # maybe change this to once we are receiving telemetry then start thread?
        vehicle.heartbeat.start()

    # -- Emergency Stop -- 
    time.sleep(3)
    Telemetry1 : Telemetry = Telemetry(CommandID=EmergencyStop.COMMAND_ID,PacketID=0, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
    Telemetry1.Vehicle = Vehicle.ERU
    SendTelemetry(Telemetry1)
    # MEA SENDS THE FLAG  PACKET_ID = 0

    # -- Add Zone --
    time.sleep(3)
    Telemetry2 : Telemetry = Telemetry(CommandID=AddZone.COMMAND_ID,PacketID=1, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
    Telemetry2.Vehicle = Vehicle.ERU
    SendTelemetry(Telemetry2)
    print("Command has been sent correctly")

    # -- Emergency Stop ALL --
    time.sleep(3)
    packet_counter = 2
    for vehicle in VEHICLE_ENUM.values():
        telemetry_instance : Telemetry = Telemetry(CommandID=EmergencyStop.COMMAND_ID,PacketID=packet_counter, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
        telemetry_instance.Vehicle = vehicle
        SendTelemetry(telemetry_instance)
        packet_counter += 1
        time.sleep(1.0)

    time.sleep(3)
    # --Add Zone ALL --
    packet_counter = 6
    for vehicle in VEHICLE_ENUM.values():
        telemetry_instance : Telemetry = Telemetry(CommandID=AddZone.COMMAND_ID,PacketID=packet_counter, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
        telemetry_instance.Vehicle = vehicle
        SendTelemetry(telemetry_instance)
        packet_counter += 1
        time.sleep(1.0)
        
    time.sleep(3)
    # -- Patient Location --
    patient_found_telemetry : Telemetry = Telemetry(CommandID=PatientLocation.COMMAND_ID, PacketID=2, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 2, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
    patient_found_telemetry.Vehicle = Vehicle.ERU
    SendTelemetry(patient_found_telemetry)
    print("Patient Location Found")
    
    time.sleep(3)
    for packet_id, ack in list(ACK_MAP.items()):
        if ack.command_id == PatientLocation.COMMAND_ID:
            patient_ack_telemetry : Telemetry = Telemetry(CommandID=PatientLocation.COMMAND_ID, PacketID=packet_id)
            patient_ack_telemetry.Vehicle = ack.vehicle_id
            SendTelemetry(patient_ack_telemetry)
            print(f"{ack.vehicle_id} patient location acknowledgement sent.")
            
    # -- Heartbeat --
    time.sleep(3)
    while not shutdown.is_set() and ACK_MAP:
        time.sleep(1)
        for packet_id, ack in list(ACK_MAP.items()):
            if ack.command_id == Heartbeat.COMMAND_ID:
                heartbeat_ack = Telemetry(CommandID=Heartbeat.COMMAND_ID, PacketID=packet_id)
                heartbeat_ack.Vehicle = ack.vehicle_id
                SendTelemetry(heartbeat_ack)
                print(f"Heartbeat ACK sent from {ack.vehicle_id}")
    # time.sleep(2)
    # Telemetry3 : Telemetry = Telemetry(CommandID=EmergencyStop.COMMAND_ID,PacketID=1, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
    # Telemetry3.Vehicle = Vehicle.MRA
    # SendTelemetry(Telemetry3)
    # print("Command has been sent correctly")
    # time.sleep(2)
    # Telemetry4  : Telemetry = Telemetry(CommandID=EmergencyStop.COMMAND_ID,PacketID=2, Speed= 100,Pitch= 0,Yaw= 0,Roll= 0, Altitude= 45, BatteryLife=0.5, LastUpdated= 0,CurrentPosition= (1, 2),VehicleStatus= 0,MessageFlag= 0, MessageLat=1.0, MessageLon=1.0, PatientStatus= 0)
    # Telemetry4.Vehicle = Vehicle.MEA
    # SendTelemetry(Telemetry4)
    # print("Command has been sent correctly")

    
    

    
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
