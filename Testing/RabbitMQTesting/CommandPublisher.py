import pika
import json
import uuid
from  Objects.command_emergency_stop import CommandInterface 
class CommandPublisher:
    """
    RabbitMQ consumer that listens to 'vehicle_commands' queue and forwards
    parsed JSON messages to a provided handler function in GCS.
    """
    def __init__(self,queue_name = 'vehicle_commands', call_back_queue_name = 'call_back_queue'):
        """
        Args:
            queue_name (str): Name of the RabbitMQ queue to subscribe to.
            call_back_queue_name (str): Name of the call_back_queue 
        """
        self.queue = queue_name
        #build credentials 
        credentials = pika.PlainCredentials("admin","admin")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials= credentials, virtual_host= '/')
        )
        self.channel = self.connection.channel()
        # command queue
        self.channel.queue_declare(queue = self.queue, durable = True)
        # The action of sending a message publishing
        self.channel.queue_declare(queue = call_back_queue_name, exclusive = True, auto_delete= True)
        self.call_back_queue_name = call_back_queue_name
        # Declare consumer for the call_back_queue
        self.channel.basic_consume(queue=self.call_back_queue_name, on_message_callback= self.on_response)
        self.response = None
    #command json string type
    def sending_command(self,command :CommandInterface):
        # generate correlation id
        # self.response = None
        # generate unique id
        self.response = None
        self.correlation_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange= '',
            routing_key= self.queue,
            # RPC stuff
            properties = pika.BasicProperties(
                reply_to= self.call_back_queue_name,
                correlation_id = self.correlation_id
            ),
            # convert command struture, into dic then int   o json string
            body = json.dumps(command.__dict__, indent= 3))

        while self.response is None:
                # this will be our blocking functionality, that will x times the time for commands
                self.connection.process_data_events(10)
        if self.response == None:
                self.response = (command.command_id, command.vehile_id, "False")
        elif self.response != None:
                self.response = (command.command_id, command.vehile_id, "True")
            

    def on_response(self,ch, method,props,body):
        ## this is gonna change
        if self.correlation_id == props.correlation_id:
            self.response = body
            # body [command_type, vehicle_id, True/False "]
     # when received the message this callback_fuction will be triggered, and
    
    
    def stop(self):
        if self.connection:
            self.connection.close()
        
    