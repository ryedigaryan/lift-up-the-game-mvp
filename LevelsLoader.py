import csv
import os
from RawLevelData import RawLevelData
from RawCustomerData import RawCustomerData
from RawSpawnLocationData import RawSpawnLocationData


class LevelsLoader:
    def __init__(self, levels_root_path):
        """
        Initializes the LevelsLoader.

        Args:
            levels_root_path (str): The root directory containing level folders.
        """
        self.levels_root_path = levels_root_path

    def load(self, level_name):
        """
        Loads a level by name.

        Args:
            level_name (str): The name of the level folder (e.g., "level_1").

        Returns:
            RawLevelData: The loaded raw level data.
        """
        level_path = os.path.join(self.levels_root_path, level_name)
        
        customer_spawns_path = os.path.join(level_path, "customer_spawns.csv")
        spawn_locations_path = os.path.join(level_path, "spawn_locations.csv")
        
        if not os.path.exists(customer_spawns_path):
            raise FileNotFoundError(f"Customer spawns file not found at {customer_spawns_path}")
            
        if not os.path.exists(spawn_locations_path):
            raise FileNotFoundError(f"Spawn locations file not found at {spawn_locations_path}")

        spawn_locations = self._load_spawn_locations(spawn_locations_path)
        customer_spawns = self._load_customer_spawns(customer_spawns_path)
        
        # Currently hardcoding num_floors to 5, but this could also be loaded from a config file
        return RawLevelData(
            customer_spawns=customer_spawns,
            spawn_locations=spawn_locations,
            num_floors=5
        )

    def _load_spawn_locations(self, file_path):
        """Loads spawn location data from a CSV file."""
        locations = {}
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    floor = int(row['Floor'])
                    x = int(row['X'])
                    if floor not in locations:
                        locations[floor] = []
                    locations[floor].append(RawSpawnLocationData(floor, x))
        except Exception as e:
            print(f"Error parsing spawn locations file: {e}")
            raise e
        return locations

    def _load_customer_spawns(self, file_path):
        """Loads customer spawn data from a CSV file."""
        spawns = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamp = float(row['Timestamp'])
                    spawn_id = row['SpawnLocation']
                    priority = row['Priority']
                    target_floor = int(row['TargetFloor'])
                    spawns.append(RawCustomerData(timestamp, spawn_id, priority, target_floor))
        except Exception as e:
            print(f"Error parsing customer spawns file: {e}")
            raise e
        return spawns
