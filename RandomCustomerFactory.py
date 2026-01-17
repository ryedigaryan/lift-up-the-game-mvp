import random
from typing import Optional
from Customer import Customer


class RandomCustomerFactory:
    def __init__(self, high_priority_prob: float = 0.5, seed: Optional[int] = None):
        self.high_priority_prob = high_priority_prob
        if seed:
            random.seed(seed)

    def generate(self, spawn_floor: int, spawn_x: int, total_floors: int, floor_width: int, request_time: float) -> Customer:
        # Randomize properties
        target_floor = self._request_random_floor(spawn_floor, total_floors)
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        popup_offset_y = random.randint(-5, 9)
        is_high_priority = random.random() < self.high_priority_prob

        # Create and return a customer instance with deterministic properties
        return Customer(
            spawn_floor=spawn_floor,
            spawn_x=spawn_x,
            floor_width=floor_width,
            target_floor=target_floor,
            color=color,
            popup_offset_y=popup_offset_y,
            is_high_priority=is_high_priority,
            request_time=request_time
        )

    def _request_random_floor(self, current_floor: int, total_floors: int) -> int:
        """Request a random floor different from current floor"""
        available_floors = [f for f in range(total_floors) if f != current_floor]
        return random.choice(available_floors)
