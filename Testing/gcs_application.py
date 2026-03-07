# This Simulates the GCS Receiving and Sending Commands to the vehicles through Software Integration
# This will only be used for Tesing Purposes when running without the GCS Applicaiton

def telemetry_listener():
    # reads telemetry from each vehicle's telemetry queue
    pass

def command_publisher():
    # sends a command into the RabbitMQ command queue
    pass

def command_manager():
    # check ack status 
    # queue timeout duration should be as long as it takes to retry the command x times
    pass

def main():
    #terminalselection UI for sending commands

    pass

if __name__ == "__main__":
    main()