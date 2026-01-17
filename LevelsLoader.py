import csv
import os
from typing import List, Dict
from RawLevelData import RawLevelData
from RawCustomerData import RawCustomerData
from RawSpawnLocationData import RawSpawnLocationData


class LevelsLoader:
    def __init__(self, levels_root_path: str):
        """
        Initializes the LevelsLoader.

        Args:
            levels_root_path (str): The root directory containing level folders.
        """
        self.levels_root_path = levels_root_path

    def level_exists(self, level_num: int) -> bool:
        """
        Checks if a level directory and its required files exist.

        Args:
            level_num (int): The number of the level.

        Returns:
            bool: True if the level exists and is valid, False otherwise.
        """
        level_name = f"level_{level_num}"
        level_path = os.path.join(self.levels_root_path, level_name)
        customer_spawns_path = os.path.join(level_path, "customer_spawns.csv")
        spawn_locations_path = os.path.join(level_path, "spawn_locations.csv")

        return (os.path.isdir(level_path) and
                os.path.exists(customer_spawns_path) and
                os.path.exists(spawn_locations_path))

    def load(self, level_num: int) -> RawLevelData:
        """
        Loads a level by name.

        Args:
            level_num (int): The number of the level.

        Returns:
            RawLevelData: The loaded raw level data.
        """
        level_name = f"level_{level_num}"
        if not self.level_exists(level_num):
            raise FileNotFoundError(f"Level '{level_name}' not found or is incomplete.")

        level_path = os.path.join(self.levels_root_path, level_name)
        customer_spawns_path = os.path.join(level_path, "customer_spawns.csv")
        spawn_locations_path = os.path.join(level_path, "spawn_locations.csv")

        spawn_locations = self._load_spawn_locations(spawn_locations_path)
        customer_spawns = self._load_customer_spawns(customer_spawns_path)
        
        # Currently hardcoding num_floors to 5, but this could also be loaded from a config file
        return RawLevelData(
            level_num=level_num,
            customer_spawns=customer_spawns,
            spawn_locations=spawn_locations,
            num_floors=5
        )

    def _load_spawn_locations(self, file_path: str) -> Dict[int, List[RawSpawnLocationData]]:
        """Loads spawn location data from a CSV file."""
        locations: Dict[int, List[RawSpawnLocationData]] = {}
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

    def _load_customer_spawns(self, file_path: str) -> List[RawCustomerData]:
        """Loads customer spawn data from a CSV file."""
        spawns: List[RawCustomerData] = []
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
