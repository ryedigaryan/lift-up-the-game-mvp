import random
from collections import deque
from Customer import Customer

class FileCustomerFactory:
    def __init__(self, raw_customer_data_list):
        """
        Initializes the factory with pre-loaded raw customer data.
        
        Args:
            raw_customer_data_list (list[RawCustomerData]): List of RawCustomerData objects.
        """
        self.spawns = {}  # Dict[spawn_id, deque of RawCustomerData]
        self._organize_spawns(raw_customer_data_list)

    def _organize_spawns(self, raw_data_list):
        for data in raw_data_list:
            if data.spawn_id not in self.spawns:
                self.spawns[data.spawn_id] = deque()
            self.spawns[data.spawn_id].append(data)
        
        # Sort spawns by timestamp for each location
        for spawn_id in self.spawns:
            self.spawns[spawn_id] = deque(sorted(self.spawns[spawn_id], key=lambda x: x.timestamp))

    def get_customer(self, spawn_id, current_time, spawn_floor, spawn_x, total_floors, floor_width):
        """
        Check if there is a customer scheduled to spawn at this location and time.
        Returns a Customer object if yes, None otherwise.
        """
        if spawn_id not in self.spawns or not self.spawns[spawn_id]:
            return None

        # Check the next scheduled spawn
        next_spawn = self.spawns[spawn_id][0]
        
        if current_time >= next_spawn.timestamp:
            # It's time to spawn!
            spawn_data = self.spawns[spawn_id].popleft()
            
            is_high_priority = (spawn_data.priority.upper() == 'HIGH')
            target_floor = spawn_data.target_floor
            
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
