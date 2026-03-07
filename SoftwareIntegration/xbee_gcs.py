# This is the main manager for all of Software Integration's duties.

VEHICLES = {}
# vehicle_name : vehicle object
#vehicles objects should have: MAC Address + Telemetry Queue Publisher + # acked, # sent, time of last heartbeat, heartbeat thread

#create a lock for sending commands & heartbeat threads. Only one can be done at a time

def telemetry_manager():
    # decodes and reads telemetry for vehicle name
    # check_ack_status
    # if check_ack_status && is command(not heartbeat)
    #   send_command_ack
    #   increment # commands acked (unique per vehicle)
    # if check_ack_status && is heartbeat
    #   increment # beats acked (unique per vehicle)
    # save time of last telemetry (unique per vehicle)
    # Vehicle.publish_telemetry()
    pass

#each vehicle will need a heartbeat manager
def heartbeat_manager():
    # sends the heartbeat once every second
    # determine_connection_status()
    # aquire lock to send command
    # send_command w/ the status (Vehicle.status)
    # release lock 
    # increment # beats sent (unique per vehicle)
    pass

def command_manager():
    # listens to commands from the command RabbitMQ queue
    # 
    # aquire lock to send command
    # send_command
    # release lock 
    # increment # command sent (unique per vehicle)
    # retry command x times if no ack
    pass

def check_ack_status():
    # reads command ack + time 
    # compare to expected time in dict
    # return True or False
    pass

def send_command_ack():
    # get temporal queue for command ack using uniqueID
    # send ack back to gcs
    pass

def send_command(command_id:int, args):
    # put unique ID into hashmap 
    # match command_id (determine which command we are sending)
    # unpack args accordingloy to each command's specfic structure & create the object given by infra (under Packet)
    # transmit command to correct MAC of the vehicle xbee
    pass

def main():
    #initialize all vehicle objects
    # start threads
    # include a gracefull shutdown when there is keyboard interrupt to clean up the threads
    pass

if __name__ == "__main__":
    main()