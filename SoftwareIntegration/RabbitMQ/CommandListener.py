import pika
import json


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
        self.global_consumer = None
    #start consuming
    def start(self) -> str:
        # self.channel.basic_qos(prefetch_count=1)
        # on_message_callback -> whenever a message has been received the function _on_messsage will be triggered
        # we need the tag to identify the consumer, since this is gonna change every time, for each command sent 
        self.channel.basic_consume(queue=self.queue, on_message_callback= self._on_message)
        print(f"[RabbitMQ] Listening on {self.queue}")
        self.channel.start_consuming()
     # when received the message this callback_fuction will be triggered, and
    def _on_message(self, ch, method,properties, body):
        """Internal callback to handle new messages."""
        try:
            msg = json.loads(body)
            print(msg)
            if self.on_command:
                self.on_command(msg)
            
            self._on_publish(self, ch,method ,properties, body)    
        except Exception as e:
            print(f"Error processing RabbitMQ messagews: {e}")
        finally:
            ch.basic_ack(method.delivery_tag)
    def stop(self):
        if self.connection:
            self.connection.close()
    # RPC STUFF:
    # The basic idea of on publish, is that whenever is validated, its gonna publish
    # the command throught that specific unique_queque
    def _on_publish(self,ch, method,properties, body):
        # acquire temporal queque and send the response
        ch.basic_publish(exchange = '',
                        routing_key = properties.reply_to,
                        properties = pika.BasicProperties(
                            correlation_id=  properties.correlation_id
                        ),
                        body = str()             
                        )
        ch.basic_ack(delivery_tag= method.delivery_tag)
        
    