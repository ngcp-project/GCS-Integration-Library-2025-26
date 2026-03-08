# This is the main manager for all of Software Integration's duties.
import Vehicle
VEHICLES = {
    # "Name of the vehicle" : "Vehicle object" 
}
# vehicle_name : vehicle object
# vehicles objects should have: MAC Address + Telemetry Queue Publisher + # acked, # sent, time of last heartbeat, heartbeat thread

#create a lock for sending commands & heartbeat threads. Only one can be done at a time
#global lock
# 1 thread for telemetry manager
def telemetry_manager():
    # extracts frame type
    # converts into a specific string format 
    # decodes to a Telemetry instance
    # and reads telemetry for vehicle name
    # extract packet_id and last_updated_time from telemetry
    # check_ack_status_var = check_ack_status(packet_id, last_updated_time)
    # if check_ack_status_var && is command(not heartbeat)
    #   send_command_ack
    #   increment # commands acked (unique per vehicle)
    # if check_ack_status_var && is heartbeat
    #   increment # beats acked (unique per vehicle)
    # save time of last telemetry (unique per vehicle)
    # vehicle.publish_telemetry()
    pass

# Each vehicle will need a heartbeat manager
def heartbeat_manager():
    # sends the heartbeat once every second
    # determine_connection_status()
    # aquire lock to send command
    # send_command w/ the status (Vehicle.status)
    # release lock 
    # increment # beats sent (unique per vehicle)
    pass
# 1 thread for commands
def command_manager():
    # listens to commands from the command RabbitMQ queue
    # aquire lock to send command
    # send_command
    # release lock 
    # increment # command sent (unique per vehicle)
    # retry command x times if no ack
    pass

def check_ack_status(packet_id : int, last_updated_time : int) -> bool:
    # reads command ack (packet_id) + last_updated 
    # packet_id : (expected time)     
    # compare to expected time in dict with packet_id and last_updated time
    # return True or False
    pass

def send_command_ack():
    # get temporal queue for command ack using packet_id
    # trigger rpc callback function send that through the temporal queque
    # send ack back to gcs
    pass

# args : any kind of parameter, not type defined
def send_command(command_id:int, args):
    # put unique ID into hashmap 
    # match command_id (determine which command we are sending) switch case
    # unpack args accordingloy to each command's specfic structure & create the object given by infra (under Packet)
    # transmit command to correct MAC of the vehicle xbee
    pass

def main():
    #initialize all vehicle objects
    # [ERU,MRA,MEA]
    # VEHICLES["ERU"] = Vehicle("arguments")
    # VEHICLES["MRA"] = Vehicle("arguments")
    # VEHICLES["MEA"] = Vehicle("arguments")
    # 3 threads hearbeat + 1 thread command_manager + 1 thread telemetry manager
    # ()
    # start threads
    pass

if __name__ == "__main__":
    main()