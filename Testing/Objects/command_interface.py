
class CommandInterface:
    def __init__(self, vehicle_id :int ,command_id : int, coordinates: None, count: int):
        self.vehile_id = vehicle_id
        self.command_id = command_id
        self.count  = count

    def increase_number_of_packets(self) -> int:
        self.count = self.count + 1
        return self.count

        

        

