from Objects.command_emergency_stop import EmergencyStopCommand
from RabbitMQTesting.CommandPublisher import CommandPublisher
import threading

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
rabbitmq_instance = CommandPublisher()
terminate_event = threading.Event()
def telemetry_listener():
    # reads telemetry from each vehicle's telemetry queue (RabbitMQ)
    pass

def command_publisher(emergency_command, rabbitmq_instance :CommandPublisher):
    rabbitmq_instance.sending_command(emergency_command) 

# this will constantly listening for comamnds
def command_manager(rabbitmq_instance: CommandPublisher):
    while not terminate_event.is_set():
        if rabbitmq_instance.response[2] == "True":
            print(f"Command: {rabbitmq_instance.response[0]} for vehicle: {rabbitmq_instance.response[1]} has been acknowledge")
        elif rabbitmq_instance.response[2] == "False":
            print(f"Command: {rabbitmq_instance.response[0]} for vehicle: {rabbitmq_instance.response[1]} has not been acknowledge")



def close_connection():
        terminate_event.set()
        # close publisher
        rabbitmq_instance.channel.close()
        
def main():
    # terminal selection UI for sending commands
    # rabbitmq_instance = CommandPublisher()
    # create separate thread that is gonna keep listening for commands
    command_manager_thread = threading.Thread(target = command_manager(rabbitmq_instance) ,daemon= True)
    command_manager_thread.start()
    try:
        while True:
            print("choose a number:")
            print(" 1 : Emergency Stop")
            choice_command_id = input("Enter a number: ")
            choice_vehicle_id = input("Enter name of vehicle: ")

            if choice_command_id.isdigit():
                if int(choice_command_id) == 1:
                    emergency_command = EmergencyStopCommand(choice_vehicle_id,int(choice_command_id))
                    # we need to publish the emergency_command:
                    command_publisher(emergency_command,rabbitmq_instance)
                elif int(choice_command_id)== 2:
                    pass
            else:
                print("Invalid input")
    except KeyboardInterrupt:
        print("\n Shutdown requested by user.")
    finally:
        close_connection()

if __name__ == "__main__":
    main()