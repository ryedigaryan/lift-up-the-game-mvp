import csv
import random
from collections import deque
from Customer import Customer
from PenaltyAttributes import PenaltyAttributes

class FileCustomerFactory:
    def __init__(self, file_path):
        self.spawns = {}  # Dict[spawn_id, deque of spawn_info]
        self._load_spawns(file_path)

    def _load_spawns(self, file_path):
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamp = float(row['Timestamp'])
                    spawn_id = row['SpawnLocation']
                    priority = row['Priority']
                    target_floor = int(row['TargetFloor'])
                    
                    if spawn_id not in self.spawns:
                        self.spawns[spawn_id] = deque()
                    
                    self.spawns[spawn_id].append({
                        'timestamp': timestamp,
                        'priority': priority,
                        'target_floor': target_floor
                    })
            
            # Sort spawns by timestamp for each location (just in case CSV is unordered)
            for spawn_id in self.spawns:
                self.spawns[spawn_id] = deque(sorted(self.spawns[spawn_id], key=lambda x: x['timestamp']))
                
        except FileNotFoundError:
            print(f"Error: Could not find spawn file {file_path}")
        except Exception as e:
            print(f"Error parsing spawn file: {e}")

    def get_customer(self, spawn_id, current_time, spawn_floor, spawn_x, total_floors, floor_width):
        """
        Check if there is a customer scheduled to spawn at this location and time.
        Returns a Customer object if yes, None otherwise.
        """
        if spawn_id not in self.spawns or not self.spawns[spawn_id]:
            return None

        # Check the next scheduled spawn
        next_spawn = self.spawns[spawn_id][0]
        
        if current_time >= next_spawn['timestamp']:
            # It's time to spawn!
            spawn_data = self.spawns[spawn_id].popleft()
            
            is_high_priority = (spawn_data['priority'].upper() == 'HIGH')
            target_floor = spawn_data['target_floor']
            
            # Generate random visual attributes
            color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            popup_offset_y = random.randint(-5, 9)
            
            return Customer(
                spawn_floor=spawn_floor,
                spawn_x=spawn_x,
                floor_width=floor_width,
                target_floor=target_floor,
                color=color,
                popup_offset_y=popup_offset_y,
                is_high_priority=is_high_priority
            )
            
        return None
