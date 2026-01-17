class RawLevelData:
    def __init__(self, customer_spawns_path, spawn_locations_data, num_floors=5):
        """
        Holds the raw data required to initialize a Level.

        Args:
            customer_spawns_path (str): Path to the CSV file containing customer spawn schedule.
            spawn_locations_data (dict): Dictionary mapping floor numbers to lists of spawn location data (e.g. {'X': 100}).
            num_floors (int): Number of floors in the level.
        """
        self.customer_spawns_path = customer_spawns_path
        self.spawn_locations_data = spawn_locations_data
        self.num_floors = num_floors
