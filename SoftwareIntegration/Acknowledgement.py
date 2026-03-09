
"""
    If we used temporal queues (short term queues), we dont need to store the correlation id for ack.
    Each command will have their own exclusive callback queue, and then its gonna be eliminated.
"""
class Acknowledgement():
    def __init__(self, expected_time:float, correlation_id:int):
        self.expected_time = expected_time
        # temporal queue (?)
        # maybe deprecate this if there are not many things to save
        pass
