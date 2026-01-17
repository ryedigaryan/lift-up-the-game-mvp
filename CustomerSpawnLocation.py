import pygame as pg
from RandomCustomerFactory import RandomCustomerFactory


class CustomerSpawnLocation:
    def __init__(self, spawn_id, floor_number, spawn_x, total_floors, floor_width, spawn_interval=60.0, start_time=None, file_factory=None):
        """
        Initialize customer spawn location

        Args:
            spawn_id: Unique identifier for this spawn location (e.g., "3-1")
            floor_number: The floor this spawn location is on
            spawn_x: X coordinate where customers spawn
            total_floors: Total number of floors in the game
            floor_width: Width of the floor (for wandering limits)
            spawn_interval: Time in seconds between spawns (default 60) - ONLY USED FOR RANDOM SPAWNING
            start_time: Time in seconds when first spawn occurs (default: floor_number * 60) - ONLY USED FOR RANDOM SPAWNING
            file_factory: Optional FileCustomerFactory instance. If provided, spawns are driven by file.
        """
        self.id = spawn_id
        self.floor_number = floor_number
        self.spawn_x = spawn_x
        self.total_floors = total_floors
        self.floor_width = floor_width
        
        self.file_factory = file_factory
        
        # Random spawning parameters (used if file_factory is None)
        self.spawn_interval = spawn_interval
        self.start_time = start_time if start_time is not None else floor_number * 60.0
        self.random_factory = RandomCustomerFactory(high_priority_prob=0.5)
        
        self.time_since_start = 0.0
        self.spawned_customers = []
        self.total_spawned_count = 0

    def update(self, dt):
        """
        Update spawn timer and spawn customers if needed

        Args:
            dt: Delta time in seconds since last update
        """
        self.time_since_start += dt

        if self.file_factory:
            # File-based spawning
            customer = self.file_factory.get_customer(
                self.id, 
                self.time_since_start, 
                self.floor_number, 
                self.spawn_x, 
                self.total_floors, 
                self.floor_width
            )
            if customer:
                self.spawned_customers.append(customer)
                self.total_spawned_count += 1
        else:
            # Random spawning (legacy behavior)
            if self.time_since_start >= self.start_time:
                time_since_first_spawn = self.time_since_start - self.start_time
                expected_total_spawns = int(time_since_first_spawn / self.spawn_interval) + 1

                while self.total_spawned_count < expected_total_spawns:
                    customer = self.random_factory.generate(
                        spawn_floor=self.floor_number,
                        spawn_x=self.spawn_x,
                        total_floors=self.total_floors,
                        floor_width=self.floor_width
                    )
                    self.spawned_customers.append(customer)
                    self.total_spawned_count += 1

    def get_active_customers(self):
        """Get list of customers that haven't been delivered yet"""
        return [c for c in self.spawned_customers if c.state != "delivered"]

    def get_all_customers(self):
        """Get all spawned customers"""
        return self.spawned_customers

    def remove_delivered_customers(self):
        """Clean up delivered customers"""
        self.spawned_customers = [c for c in self.spawned_customers if c.state != "delivered"]
