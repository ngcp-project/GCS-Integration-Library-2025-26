from Objects.command_interface import CommandInterface

class EmergencyStopCommand(CommandInterface):
    def __init__(self, vehicle_id : str, command_id: int):
        super().__init__(vehicle_id= vehicle_id, command_id= command_id)
    
    
    