"""
    (GCS_APPLICATION)
    
- This Simulates the GCS Receiving and Sending Commands to the vehicles through Software Integration
- This will only be used for Tesing Purposes when running without the GCS-Desktop-Application and readibility
"""
"""
- Flow of data:
    * Initiliaze 1 listener for testing, GCS-Desktop creates a consumer for each vehicle
    * 1 thread that is constantly listening telemetry
    * 1 thread that is gonna constantly listening to the command acknowledgment idk/ depends how frequent we sent commands
"""
def telemetry_listener():
    # reads telemetry from each vehicle's telemetry queue (RabbitMQ)
    pass

def command_publisher():
    # sends a command into the RabbitMQ command queue
    # creation of the rpc stuff:
        # creates the temporal queue
        # we need to trigger the start consuming that is gonna have the temporal queue (start thread)
        # send the command through the command_queue
    
        
    pass

def command_manager(): 
    # check ack status 
    # queue timeout duration should be as long as it takes to retry the command x times
    # somehow acquire the consumer tag.
    # trigger basic_cancel(consumer tag) this will cancel stop listening to commands deleteting the temporal queue
    # trigger stop_consuming this will actually close the  the infinite loop of consumption, ending the thread
    pass


def main():
    # terminal selection UI for sending commands

    # for example 1 -> emergency stop
    # if value == 1:
        #  command =  Emegerncy stop type stucture
    # triger command_publisher(command)
    pass

if __name__ == "__main__":
    main()