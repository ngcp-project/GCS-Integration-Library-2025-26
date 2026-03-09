# This is the main manager for all of Software Integration's duties.
from datetime import datetime
import threading
import time
from SoftwareIntegration.Vehicle import Vehicle
from SoftwareIntegration.RabbitMQ.TelemetryPublisher import TelemetryPublisher
from SoftwareIntegration.RabbitMQ.CommandListener import CommandListener

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

# 1 thread for telemetry manager
def telemetry_manager() -> None:
    print(f"Telemetry Manager Started")
    while not shutdown.is_set():
        print(ACK_MAP)
        time.sleep(3)
        pass
    
        # subscribe to telemetry_infra (may change depending on approach)
        # check telemetry for command ack
            # use an enum for knowing which vehicle it is 

            # ack_status = check_ack_status(telemetry.packetId, telemetry.last_updated)

            # if ack_status && is command(not heartbeat)
            #   send_command_ack() (to gcs in temporal queue)
            #   increment # commands acked (unique per vehicle)
            # if ack_status && is heartbeat
            #   increment # beats acked (unique per vehicle)
            # save time of last telemetry (unique per vehicle)

        # publish telemetry to telemetry_gcs using vehicle object

    print(f"Telemetry Manager Shutting Down")

# Each vehicle will need a heartbeat manager
def heartbeat_manager(vehicle: Vehicle) -> None:
    # sends the heartbeat once every second
    while not shutdown.is_set():
        print(f"Heartbeat for {vehicle.name}")
        vehicle.determine_connection_status()

        with command_lock:
            send_command(command_id=0, args=vehicle.status, destination=vehicle.name)
            vehicle.num_beats_sent += 1

        time.sleep(3) 
    
    print(f"{vehicle.name} sent {vehicle.num_beats_sent} beats")
    print(f"Heartbeat for {vehicle.name} Shutting Down")

# 1 thread for commands
# def command_manager(command_listener: CommandListener) -> None:
def command_manager() -> None:
    print(f"Command Manager Started")
    send_command(command_id=1, args="testing", destination="BOB")
    while not shutdown.is_set():
        # listens to commands from the command RabbitMQ queue

        with command_lock:
            pass
            # aquire lock to send command
            # send_command
            # update last_command_time
            # update last_command_sent
            # release lock 
            # increment # command sent (unique per vehicle)

        # check which commands need to be resent (wip, it's kinda botched lmao)
        # might refactor the check_ack_status 
        # for vehicle in VEHICLES
            #if vehicle.last_command_sent == None or datetime.now() - vehicle.last_command_time <= x seconds: 
                #continue

            # if num_command_sent > 10 && num_command_ack == 0  (retry failed)
                #reset counters
                #vehicle.last_command_sent = None
            # else 
                # update last_command_time
                #retry vehicle.last_command_sent (maybe make into enum?)
                # increment counters
    print(f"Command Manager Shutting Down")

def check_ack_status(packet_id : int, command_ack:int, time_arrived : float) -> bool:
    # expected_ack = ACK_MAP[packet_id]
    # last_updated should be a float bc it is datetime.datetime()? and it's already in seconds
    # compare to expected_time in expected_ack with time_arrived and command_id
    # return True or False
    pass

def send_command_ack():
    # get temporal queue for command ack using packet_id
    # trigger rpc callback function send that through the temporal queque
    # send ack back to gcs
    pass

# args : any kind of parameter, not type defined
def send_command(command_id:int, destination, args):
    global packet_id
    print(f"Sending Command {command_id} with args of {args} to {destination}")
    ACK_MAP[packet_id] = f"Command {command_id} with args of {args} to {destination}"
    packet_id+=1
    # put packet_id into hashmap 
    # match command_id (determine which command we are sending) switch case
    # unpack args accordingloy to each command's specfic structure & create the object given by infra (under Packet)
    # transmit command to correct MAC of the vehicle xbee
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
    vehicle_list = ["ERU", "MRA", "MEA"]

    #initialize all vehicle objects
    for vehicle in vehicle_list:
        vehicle = Vehicle(name=vehicle)
        # vehicle.telemetry_publisher = TelemetryPublisher(vehicleName=vehicle.name, hostname='localhost'),
        vehicle.heartbeat=threading.Thread(target=heartbeat_manager, args=[vehicle])
        VEHICLES[vehicle.name] = vehicle

    # 3 threads hearbeat + 1 thread command_manager + 1 thread telemetry manager
    # command_manager_thread = threading.Thread(target=command_manager, args=CommandListener())
    command_manager_thread = threading.Thread(target=command_manager)
    telemetry_manager_thread = threading.Thread(target=telemetry_manager)

    # start threads
    telemetry_manager_thread.start()
    command_manager_thread.start()
    for vehicle in VEHICLES.values():
        vehicle.heartbeat.start()
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