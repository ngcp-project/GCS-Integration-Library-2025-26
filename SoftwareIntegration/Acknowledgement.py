from Enum import Vehicle

class Acknowledgement():
    WAITTIMEINSECONDS = 1
    def __init__(self, command_id: int, vehicle_id : Vehicle, time:float):
        self.command_id = command_id
        self.vehicle_id = vehicle_id
        self.time = time + Acknowledgement.WAITTIMEINSECONDS
















