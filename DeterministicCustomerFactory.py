import random
from collections import deque
from typing import List, Dict, Optional
from Customer import Customer
from RawCustomerData import RawCustomerData


class DeterministicCustomerFactory:
    def __init__(self, raw_customer_data_list: List[RawCustomerData]):
        """
        Initializes the factory with pre-loaded raw customer data.
        
        Args:
            raw_customer_data_list (list[RawCustomerData]): List of RawCustomerData objects.
        """
        self.spawns: Dict[str, deque[RawCustomerData]] = {}
        self._organize_spawns(raw_customer_data_list)

    def _organize_spawns(self, raw_data_list: List[RawCustomerData]):
        for data in raw_data_list:
            if data.spawn_id not in self.spawns:
                self.spawns[data.spawn_id] = deque()
            self.spawns[data.spawn_id].append(data)
        
        # Sort spawns by timestamp for each location
        for spawn_id in self.spawns:
            self.spawns[spawn_id] = deque(sorted(self.spawns[spawn_id], key=lambda x: x.timestamp))

    def get_customer(self, spawn_id: str, current_time: float, spawn_floor: int, spawn_x: int, total_floors: int, floor_width: int) -> Optional[Customer]:
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
                is_high_priority=is_high_priority,
                request_time=current_time
            )
            
        return None

    def remaining_customers_to_spawn(self) -> int:
        """
        Returns the total number of customers that have not yet been spawned.
        """
        return sum(len(queue) for queue in self.spawns.values())
