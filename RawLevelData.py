from typing import List, Dict
from RawCustomerData import RawCustomerData
from RawSpawnLocationData import RawSpawnLocationData


class RawLevelData:
    def __init__(self, customer_spawns: List[RawCustomerData], spawn_locations: Dict[int, List[RawSpawnLocationData]], num_floors: int = 5):
        """
        Holds the raw data required to initialize a Level.

        Args:
            customer_spawns (list[RawCustomerData]): List of customer spawn events.
            spawn_locations (dict[int, list[RawSpawnLocationData]]): Dictionary mapping floor numbers to lists of spawn location data.
            num_floors (int): Number of floors in the level.
        """
        self.customer_spawns = customer_spawns
        self.spawn_locations = spawn_locations
        self.num_floors = num_floors
