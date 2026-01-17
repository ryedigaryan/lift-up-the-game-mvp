from typing import List, Dict, Optional, Set
import pygame as pg
from Customer import Customer
from Floor import Floor


class Lift:
    def __init__(self, name: str, x: int, total_floors: int, floor_height: int, floors: Optional[List[Floor]] = None, top_padding: int = 0):
        self.name = name
        self.x = x
        self.width = 60
        self.height = 80
        self.current_floor = 0
        self.customers_inside: List[Customer] = []
        self.waiting_customers: Dict[int, List[Customer]] = {}
        self.request_queue: List[int] = []
        self.state = "idle"  # "idle", "moving_up", "moving_down", "waiting"
        self.direction = "up"
        self.speed = 2.5
        self.total_floors = total_floors
        self.floor_height = floor_height
        self.top_padding = top_padding
        self.y = self._floor_to_y(0)
        self.door_open = False
        self.door_timer = 0.0
        self.door_wait_time = 2.0
        self.floors: List[Floor] = floors or []
        self.stop_list_font = pg.font.Font(None, 18)
        self.target_sequence: List[int] = []

    def _floor_to_y(self, floor: int) -> int:
        ground_height = 10
        return self.top_padding + (self.total_floors - 1 - floor) * self.floor_height + self.floor_height - ground_height - self.height

    def _y_to_floor(self) -> int:
        for floor in range(self.total_floors):
            floor_y = self._floor_to_y(floor)
            if abs(self.y - floor_y) < 5:
                return floor
        return self.current_floor

    def add_customer_request(self, customer: Customer):
        if customer.current_floor not in self.waiting_customers:
            self.waiting_customers[customer.current_floor] = []
        if customer.current_floor not in self.request_queue:
            self.request_queue.append(customer.current_floor)

        self.waiting_customers[customer.current_floor].append(customer)

        if self.state == "idle":
            self._update_target_sequence()
        else:
            self._update_target_sequence()

    def update(self, dt: float, level_time: float):
        if self.state == "idle":
            if self.target_sequence:
                self._start_moving(level_time)
        elif self.state == "waiting":
            self.door_timer += dt
            if self.door_timer >= self.door_wait_time:
                self._close_door_and_continue(level_time)
        elif self.state in ["moving_up", "moving_down"]:
            self._move_towards_target(level_time)

    def _set_idle(self):
        self.state = "idle"
        self.target_sequence = []

    def _start_moving(self, level_time: float):
        if not self.target_sequence:
            self._set_idle()
            return

        next_floor = self._get_next_floor()
        if next_floor is None:
            self._set_idle()
            return
            
        target_y = self._floor_to_y(next_floor)

        if abs(self.y - target_y) < 5:
            self._arrive_at_floor(level_time)
        else:
            if self.y > target_y:
                self.state = "moving_up"
                self.direction = "up"
            else:
                self.state = "moving_down"
                self.direction = "down"

    def _get_next_floor(self) -> Optional[int]:
        """The next floor is simply the first one in our sequence."""
        return self.target_sequence[0] if self.target_sequence else None

    def _find_best_stop(self, current_floor: int, direction: str, delivery_floors: Set[int], waiting_customers: Dict[int, List[int]], request_queue: List[int]) -> Optional[int]:
        """Pure function to find the single best next stop."""
        if not delivery_floors:
            return request_queue[0] if request_queue else None

        if direction == "up":
            deliveries_above = [f for f in delivery_floors if f > current_floor]
            if deliveries_above:
                limit = max(deliveries_above)
                pickups_on_way = [f for f, targets in waiting_customers.items() if current_floor < f <= limit and any(t > f for t in targets)]
                return min(deliveries_above + pickups_on_way)
            else:
                deliveries_below = [f for f in delivery_floors if f < current_floor]
                if not deliveries_below: return None
                limit = min(deliveries_below)
                pickups_on_way = [f for f, targets in waiting_customers.items() if limit <= f < current_floor and any(t < f for t in targets)]
                return max(deliveries_below + pickups_on_way)
        else:  # "down"
            deliveries_below = [f for f in delivery_floors if f < current_floor]
            if deliveries_below:
                limit = min(deliveries_below)
                pickups_on_way = [f for f, targets in waiting_customers.items() if limit <= f < current_floor and any(t < f for t in targets)]
                return max(deliveries_below + pickups_on_way)
            else:
                deliveries_above = [f for f in delivery_floors if f > current_floor]
                if not deliveries_above: return None
                limit = max(deliveries_above)
                pickups_on_way = [f for f, targets in waiting_customers.items() if current_floor < f <= limit and any(t > f for t in targets)]
                return min(deliveries_above + pickups_on_way)

    def _update_target_sequence(self):
        """Calculates the entire optimal sequence of stops and stores it."""
        # The set of all floors that need to be visited
        all_target_floors = set(self.request_queue) | set(c.target_floor for c in self.customers_inside)
        if not all_target_floors:
            self.target_sequence = []
            return

        sim_floor = self.current_floor
        sim_direction = self.direction
        sim_deliveries = set(c.target_floor for c in self.customers_inside)
        sim_waiting = {f: [c.target_floor for c in v] for f, v in self.waiting_customers.items()}
        sim_requests = list(self.request_queue)

        sequence = []
        while sim_deliveries or sim_requests:
            next_stop = self._find_best_stop(sim_floor, sim_direction, sim_deliveries, sim_waiting, sim_requests)

            if next_stop is None: break
            sequence.append(next_stop)

            if next_stop > sim_floor: sim_direction = "up"
            elif next_stop < sim_floor: sim_direction = "down"
            sim_floor = next_stop

            sim_deliveries.discard(sim_floor)

            if sim_floor in sim_waiting:
                pickup_targets = [t for t in sim_waiting[sim_floor] if (sim_direction == "up" and t > sim_floor) or (sim_direction == "down" and t < sim_floor)]
                if not sim_deliveries: pickup_targets = sim_waiting[sim_floor]
                sim_deliveries.update(pickup_targets)
                sim_waiting.pop(sim_floor, None)

            if sim_floor in sim_requests:
                sim_requests.remove(sim_floor)

        self.target_sequence = sequence

    def _move_towards_target(self, level_time: float):
        next_floor = self._get_next_floor()
        if next_floor is None:
            self._set_idle()
            return
            
        target_y = self._floor_to_y(next_floor)
        if abs(self.y - target_y) < self.speed:
            self.y = target_y
            self._arrive_at_floor(level_time)
        else:
            if self.y > target_y: self.y -= self.speed
            else: self.y += self.speed

    def _arrive_at_floor(self, level_time: float):
        self.current_floor = self._y_to_floor()

        self.door_open = True
        self.state = "waiting"
        self.door_timer = 0

        # Drop off customers
        customers_to_remove = []
        for customer in self.customers_inside:
            if customer.target_floor == self.current_floor:
                target_spawn_x = self.x + self.width // 2
                if self.floors and self.current_floor < len(self.floors):
                    target_spawn_x = self.floors[self.current_floor].get_spawn_location_x()
                customer.exit_lift(self.current_floor, self.x + self.width // 2, target_spawn_x, level_time)
                if self.floors and self.current_floor < len(self.floors):
                    self.floors[self.current_floor].add_customer(customer)
                customers_to_remove.append(customer)
        for customer in customers_to_remove:
            self.customers_inside.remove(customer)

        # Pick up customers
        if self.current_floor in self.waiting_customers:
            customers_to_pickup = []
            if self.customers_inside:
                for customer in self.waiting_customers[self.current_floor]:
                    if customer.state == "waiting_at_lift":
                        if self.direction == "up" and customer.target_floor > self.current_floor:
                            customers_to_pickup.append(customer)
                        elif self.direction == "down" and customer.target_floor < self.current_floor:
                            customers_to_pickup.append(customer)
            else:
                customers_to_pickup = [c for c in self.waiting_customers[self.current_floor] if c.state == "waiting_at_lift"]

            for customer in customers_to_pickup:
                if self.floors and customer.current_floor < len(self.floors):
                    self.floors[customer.current_floor].remove_customer(customer)
                customer.enter_lift()
                self.customers_inside.append(customer)

            self.waiting_customers[self.current_floor] = [c for c in self.waiting_customers[self.current_floor] if c.state != "in_lift"]
            if not self.waiting_customers[self.current_floor]:
                del self.waiting_customers[self.current_floor]
                if self.current_floor in self.request_queue:
                    self.request_queue.remove(self.current_floor)

        self._update_target_sequence()

    def _has_customers_still_walking_to_current_floor(self) -> bool:
        if self.current_floor in self.waiting_customers:
            return any(c.state == "walking_to_lift" for c in self.waiting_customers[self.current_floor])
        return False

    def _close_door_and_continue(self, level_time: float):
        if self._has_customers_still_walking_to_current_floor():
            self.door_timer = 0
            return

        self.door_open = False
        if self.target_sequence:
            self._start_moving(level_time)
        else:
            self._set_idle()

    def draw(self, screen: pg.Surface):
        color = (100, 200, 100) if self.name == "A" else (200, 100, 100)
        shaft_color = (200, 200, 200)
        for floor_num in range(self.total_floors):
            floor_y = self.top_padding + (self.total_floors - 1 - floor_num) * self.floor_height + self.floor_height - self.height - 10
            pg.draw.rect(screen, shaft_color, (self.x - 5, floor_y, self.width + 10, self.height), 1)

        pg.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        if self.door_open:
            door_color = (255, 255, 100)
            pg.draw.rect(screen, door_color, (self.x + 5, self.y + 5, self.width - 10, 5))

        font = pg.font.Font(None, 36)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

        if self.customers_inside:
            count_font = pg.font.Font(None, 24)
            count_text = count_font.render(f"{len(self.customers_inside)}", True, (255, 255, 255))
            screen.blit(count_text, (self.x + 5, self.y + self.height - 25))
            
        # Draw the first 5 stops from the data store
        if self.target_sequence:
            for i, floor_num in enumerate(self.target_sequence[:5]):
                y_offset = self.height - (i * 15) - 15
                stop_text = self.stop_list_font.render(str(floor_num), True, (255, 255, 255))
                screen.blit(stop_text, (self.x + self.width - 15, self.y + y_offset))
