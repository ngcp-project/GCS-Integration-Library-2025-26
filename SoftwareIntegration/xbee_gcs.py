# This is the main manager for all of Software Integration's duties.
from datetime import datetime
import threading
import time
from SoftwareIntegration.Vehicle import Vehicle
from SoftwareIntegration.RabbitMQ.TelemetryPublisher import TelemetryPublisher
from SoftwareIntegration.RabbitMQ.CommandListener import CommandListener
from SoftwareIntegration.Acknowledgement import Acknowledgement
from Command.EmergencyStop import EmergencyStop
from SoftwareIntegration.RabbitMQ.CommandListener import *
from Enum import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Infrastructure import GCSXBee
from Infrastructure import *
from Infrastructure.GCSXBee import *

VEHICLES = {
    # "Vehicle Name" : "Vehicle object" 
}

ACK_MAP = {
    # packet_id : "Acknowledgement object" 
}

#temp packet_id for proof of concept
packet_id = 0

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
        print(ACK_MAP)
        # check telemetry for command ack
        # use an enum for knowing which vehicle it is 
        telemetry_instance = ReceiveTelemetry() 
        packet_id = telemetry_instance.packet_id
        if packet_id in ACK_MAP:
            ack_event =  ACK_MAP[packet_id]
            vehicle_id, command_id = ack_event.vehicle_id, ack_event.command_id
            ack_status = check_ack_status(telemetry_instance.packetId, telemetry_instance.last_updated)
            vehicle_instance = VEHICLES[vehicle_id]
            if ack_status and (command_id == 2 or command_id == 3 or command_id == 4 or command_id == 5 or command_id ==6):
                send_command_ack(vehicle_id=vehicle_id, command_id= command_id)
                vehicle_instance.increment_num_command_ack()
            elif ack_status and command_id == 1:
                vehicle_instance.increment_num_beats_ack()
                vehicle_instance.last_telemetry_ack = telemetry_instance
        else:
            print(f"packet_id not found in map")

    print(f"Telemetry Manager Shutting Down")

# Each vehicle will need a heartbeat manager
def heartbeat_manager(vehicle: Vehicle) -> None:
    # sends the heartbeat once every second
    while not shutdown.is_set():
        print(f"Heartbeat for {vehicle.name}")
        vehicle.determine_connection_status()

        with command_lock:
            send_command(command_id=0, vehicle_id= vehicle.name, args = any)
            vehicle.num_beats_sent += 1

        time.sleep(3) 
    
    print(f"{vehicle.name} sent {vehicle.num_beats_sent} beats")
    print(f"Heartbeat for {vehicle.name} Shutting Down")

# 1 thread for commands
# def command_manager(command_listener: CommandListener) -> None:
def command_manager(message : dict) -> None:
    # print(f"Command Manager Started")
    # send_command(command_id=1, args="testing", destination="BOB")
    vehicle_id = message.get("vehicle_id")
    command_id = message.get("command_id")
    vehicle_instance = VEHICLES[vehicle_id]
    with command_lock:
        send_command(vehicle_id, command_id, any, message)
        vehicle_instance.increment_num_command_sent()

        # might refactor the check_ack_status 
    print(f"Command Manager Shutting Down")

def check_ack_status(packet_id : int, command_ack:int, time_arrived : float) -> bool:
    # expected_ack = ACK_MAP[packet_id]
    # last_updated should be a float bc it is datetime.datetime()? and it's already in seconds
    # compare to expected_time in expected_ack with time_arrived and command_id
    # return True or False
    pass

def send_command_ack(vehicle_id : str, command_id : str) -> None:
    #Trigger 
    consumer.resolve_ack(vehicle_id= vehicle_id, command_id= command_id)
    pass

# args : any kind of parameter, not type defined
def send_command(command_id:int, vehicle_id: str, args: dict):
    global packet_id
    print(f"Sending Command {command_id} with args of {args} to {vehicle_id}")
    ACK_MAP[packet_id] = f"Command {command_id} with args of {args} to {vehicle_id}"
    packet_id+=1
    # put packet_id into hashmap
    command_interface = None
    match command_id:
        case 2:
            command_interface = EmergencyStop(1)
            pass
        case 1:
            pass
        case 3:
            pass
    packet_id = command_interface.PacketID
    ACK_MAP[packet_id] = Acknowledgement(command_id= command_id, vehicle_id= vehicle_id, expected_time= time.time())
    if vehicle_id == "MRA":
        vehicle_name = Vehicle.MRA.name #I dont know exactly what are you suppose to sent / name?
    #Infra function to send to the queue
    SendCommand(command_interface,VehicleName=vehicle_name)
    pass

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
    vehicle_list = ["ERU", "MRA", "MEA"]

    #initialize all vehicle objects
    for vehicle in vehicle_list:
        vehicle = Vehicle(name=vehicle)
        # vehicle.telemetry_publisher = TelemetryPublisher(vehicleName=vehicle.name, hostname='localhost'),
        vehicle.heartbeat=threading.Thread(target=heartbeat_manager, args=[vehicle])
        # putting in the map vehicle name and Vehicle class
        VEHICLES[vehicle.name] = vehicle

    # 3 threads hearbeat + 1 thread command_manager + 1 thread telemetry manager
    # command_manager_thread = threading.Thread(target=command_manager, args=CommandListener())
    # Declare consumer, declare which function they are gonna use whenever they receive a message
    consumer = CommandListener(
        on_command= command_manager
    )
    # Initialize consumer listener, on_command = handle_ui_command 
    # Declare command_manager thread, actually starting consuming
    command_manager_thread = threading.Thread(target=consumer.start, args=[consumer],daemon= False)

    telemetry_manager_thread = threading.Thread(target=telemetry_manager)

    # start threads
    telemetry_manager_thread.start()
    command_manager_thread.start()
    for vehicle in VEHICLES.values():
        # for each vehicle you are gonna start the hearbeat
        vehicle.heartbeat.start()
        # skiping heartbeats?
        time.sleep(0.25) #staggers the heartbeats 

    #graceful shutdown
    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("\n Shutdown requested by user.")
    finally:
        end_program(command_manager_thread, telemetry_manager_thread)

if __name__ == "__main__":
    main()
