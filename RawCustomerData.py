class RawCustomerData:
    def __init__(self, timestamp: float, spawn_id: str, priority: str, target_floor: int):
        """
        Holds raw data for a single customer spawn event.

        Args:
            timestamp (float): Time in seconds when the customer should spawn.
            spawn_id (str): ID of the spawn location (e.g., "0-1").
            priority (str): Priority of the customer ("HIGH" or "LOW").
            target_floor (int): The destination floor.
        """
        self.timestamp = timestamp
        self.spawn_id = spawn_id
        self.priority = priority
        self.target_floor = target_floor
