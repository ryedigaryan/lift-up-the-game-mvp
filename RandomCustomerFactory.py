import random
from RandomFloorRequestingCustomer import RandomFloorRequestingCustomer
from PenaltyAttributes import PenaltyAttributes

class RandomCustomerFactory:
    def __init__(self, high_priority_prob=0.5, seed=None):
        self.high_priority_prob = high_priority_prob
        if seed:
            random.seed(seed)

    def generate(self, spawn_floor, spawn_x, total_floors, floor_width):
        # Randomize properties
        target_floor = self._request_random_floor(spawn_floor, total_floors)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        popup_offset_y = random.randint(0, 30)
        is_high_priority = random.random() < self.high_priority_prob

        # Create and return a customer instance with deterministic properties
        return RandomFloorRequestingCustomer(
            spawn_floor=spawn_floor,
            spawn_x=spawn_x,
            total_floors=total_floors,
            floor_width=floor_width,
            target_floor=target_floor,
            color=color,
            popup_offset_y=popup_offset_y,
            is_high_priority=is_high_priority
        )

    def _request_random_floor(self, current_floor, total_floors):
        """Request a random floor different from current floor"""
        available_floors = [f for f in range(total_floors) if f != current_floor]
        return random.choice(available_floors)
