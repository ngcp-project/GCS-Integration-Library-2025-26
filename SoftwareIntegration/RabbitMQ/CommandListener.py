import pika
import json
import time
import threading
class CommandListener:
    """
    RabbitMQ consumer that listens to 'vehicle_commands' queue and forwards
    parsed JSON messages to a provided handler function in GCS.
    """
    def __init__(self,queue_name = 'vehicle_commands', on_command = None):
        """
        Args:
            queue_name (str): Name of the RabbitMQ queue to subscribe to.
            on_command (callable): Handler function to call with the command JSON.
        """
        self.queue = queue_name
        self.on_command = on_command

        #build credentials 
        credentials = pika.PlainCredentials("admin","admin")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials= credentials, virtual_host= '/')
        )
        self.channel = self.connection.channel()
        # command queue
        self.channel.queue_declare(queue = self.queue, durable = True)
        self.channel.queue_declare(queue = "command_ack", durable= True)
        self.on_rpc_response = None
        self.pending_event = {}
    #start consuming
    def start(self) -> str:
        # we ensure that only 1 command is process until there is an ack, so we could avoid overwrite
        self.channel.basic_qos(prefetch_count=1)
        # on_message_callback -> whenever a message has been received the function _on_messsage will be triggered
        # we need the tag to identify the consumer, since this is gonna change every time, for each command sent 
        self.channel.basic_consume(queue=self.queue, on_message_callback= self._on_message)
        print(f"[RabbitMQ] Listening on {self.queue}")
        self.channel.start_consuming()
     # when received the message this callback_fuction will be triggered, and
    def _on_message(self, ch, method,properties, body):
        """Internal callback to handle new messages."""
        # conver back to dictionry
        # decode the structure into a json string
        #  convert into a string
        msg = json.loads(body)
        event_key = f"{msg.get('vehicle_id')}_{msg.get('command_id')}"
        event = threading.Event()
        self.pending_event[event_key] = event
        success = False
        for _ in range(10):
            self.on_command(msg)
            # waits for the internal flag to be true
            success = event.wait(timeout=2)
            if success:
                print(f"ACK has been received accordingly {event_key}")
                break

        self._on_publish(ch, method, properties,success, msg)
        self.pending_event.pop(event_key, None)

    def resolve_ack(self, vehicle_id : str, command_id:int): 
        event_key = f"{vehicle_id}_{command_id}"
        event =  self.pending_event.get(event_key)
        # if there is an event
        if event:
            #set internal flag to true
            event.set()
        else:
            print(f"Key is not existant")
    def stop(self):
        if self.connection:
            self.connection.close(), 
    def _on_publish(self,ch, method,properties, success, msg):
        response_back = {
            "vehicle_id": msg.get("vehicle_id"),
            "command_id": msg.get("command_id"),
            "status": True if success else False
        }
        print(response_back)
        json_string = json.dumps(response_back)
        response_back = json_string.encode('utf-8')
        ch.basic_publish(exchange = '',
                        routing_key = "command_ack",
                        body = response_back            
                        )
        print("Command ack has been send")
        ch.basic_ack(delivery_tag= method.delivery_tag)
        
    
    ## Command Consumer/Listener
    ## flow of the data "True" or "False" -> converted into a sequence of bytes
    ## check correlation id
    ## assign body to be -> encoded(True/False)

    ## Command Publisher/
    ## 