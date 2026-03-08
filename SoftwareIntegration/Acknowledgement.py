
"""
    If we used temporal queues (short term queues), we dont need to store the correlation id for ack.
    Each command will have their own exclusive callback queue, and then its gonna be eliminated.
"""
class Acknowledgement():
    def __init__(self, command_id:int, time, correlation_id:int):
        self.command_id = command_id
        self.time = time
        pass
