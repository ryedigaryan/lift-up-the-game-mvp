class RawLevelData:
    def __init__(self, customer_spawns, spawn_locations, num_floors=5):
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
