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

#create a lock for sending commands & heartbeat threads. Only one can be done at a time
#global lock
command_lock = threading.Lock()

#event for graceful shutdown of program
shutdown = threading.Event()

# 1 thread for telemetry manager
def telemetry_manager() -> None:
    while not shutdown.is_set():
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

    pass

# Each vehicle will need a heartbeat manager
def heartbeat_manager(vehicle: Vehicle) -> None:
    while not shutdown.is_set():
        # sends the heartbeat once every second
        # determine_connection_status()
        with command_lock:
            pass
            # aquire lock to send command
            # send_command w/ the status (Vehicle.status)
            # release lock 
            # increment # beats sent (unique per vehicle)
    pass

# 1 thread for commands
def command_manager(command_listener: CommandListener) -> None:
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
    pass

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
def send_command(command_id:int, args):
    # put packet_id into hashmap 
    # match command_id (determine which command we are sending) switch case
    # unpack args accordingloy to each command's specfic structure & create the object given by infra (under Packet)
    # transmit command to correct MAC of the vehicle xbee
    pass

def end_program():
    shutdown.set()

    # for vehicle in VEHICLES:
    #     vehicle.telemetry_publisher.close_connection()
    
    print("Shutdown complete.")
    pass

# we also need a function to clean up the dict/remove acknwoledged commands

def main():
    #initialize all vehicle objects
    # [ERU,MRA,MEA]
    # VEHICLES["ERU"] = Vehicle("arguments")
    # VEHICLES["MRA"] = Vehicle("arguments")
    # VEHICLES["MEA"] = Vehicle("arguments")
    # Initialize CommandListener and TelemetryPublisher
    # 3 threads hearbeat + 1 thread command_manager + 1 thread telemetry manager
    # ()
    # start threads

    #graceful shutdown
    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("\n Shutdown requested by user.")
    finally:
        end_program()

if __name__ == "__main__":
    main()