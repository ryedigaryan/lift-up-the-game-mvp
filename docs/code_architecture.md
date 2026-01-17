# Code Architecture

## Overview
The Lift Up Game is a Pygame-based simulation where the player manages elevators to transport customers between floors efficiently, minimizing penalties based on wait times.

## Key Components

### Main Game Loop (`main.py`)
- **`LiftUpGame`**: The central controller. Initializes Pygame, creates `Floor` and `Lift` objects, manages the event loop, and updates all game entities.
- **`StatusBar`**: Displays the total accumulated penalty at the bottom of the screen.

### Entities

#### Lift (`Lift.py`)
- Represents an elevator.
- **State Machine**: `idle`, `moving_up`, `moving_down`, `waiting` (door open).
- **Logic**: Uses a target sequence algorithm (`_find_best_stop`) to determine the most efficient path to serve requests and passengers.

#### Floor (`Floor.py`)
- Represents a building level.
- Contains `CustomerSpawnLocation`s.
- Manages customers currently on that floor (both spawning and those who arrived via lift).

#### Customer (`Customer.py`)
- Represents a passenger.
- **State Machine**: `waiting_for_lift_selection`, `walking_to_lift`, `waiting_at_lift`, `in_lift`, `exiting_lift`, `delivered`.
- **Attributes**: Priority (High/Normal), Target Floor, Penalty calculation logic.

#### Spawning System
- **`CustomerSpawnLocation.py`**: Manages timing for spawning customers on a specific floor.
- **`RandomCustomerFactory.py`**: Generates `Customer` instances with random attributes (target floor, priority).

### UI & Interaction
- **Popups**:
    - `FloorRequestPopup`: Allows player to assign Lift A or B.
    - `ServedCustomerInfoPopup`: Shows status while waiting.
    - `DeliveredCustomerPopup`: Shows final stats upon delivery.
- **Input**: Mouse clicks are detected in `main.py` and delegated to active customers/popups.

## Diagrams

### Class Diagram

```mermaid
classDiagram
    class LiftUpGame {
        +run()
        +update()
        +draw()
    }
    class Lift {
        +update()
        +add_customer_request()
        -_find_best_stop()
    }
    class Floor {
        +update()
        +get_all_customers()
    }
    class Customer {
        +state
        +target_floor
        +calculate_penalty()
    }
    class CustomerSpawnLocation {
        +update()
    }
    class StatusBar {
        +add_penalty()
    }

    LiftUpGame *-- "2" Lift
    LiftUpGame *-- "5" Floor
    LiftUpGame *-- StatusBar
    Floor *-- CustomerSpawnLocation
    CustomerSpawnLocation ..> Customer : Creates
    Lift o-- Customer : Transports
    Floor o-- Customer : Contains
```

### Customer Lifecycle Sequence

```mermaid
sequenceDiagram
    participant Game
    participant Spawner
    participant Customer
    participant Player
    participant Lift

    Game->>Spawner: update(dt)
    Spawner->>Customer: create()
    Customer->>Game: Appears on Floor
    Player->>Customer: Click Popup (Select Lift A)
    Customer->>Lift: add_customer_request()
    Customer->>Customer: State: walking_to_lift
    loop Pathfinding
        Lift->>Lift: _find_best_stop()
        Lift->>Lift: Move to Floor
    end
    Lift->>Customer: Arrive (Open Door)
    Customer->>Lift: Enter
    Customer->>Customer: State: in_lift
    Lift->>Lift: Move to Target Floor
    Lift->>Customer: Arrive (Open Door)
    Customer->>Floor: Exit
    Customer->>Customer: State: delivered
    Customer->>Game: Calculate Penalty
```

### Lift State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Moving : Request Received
    Moving --> Waiting : Arrive at Floor
    Waiting --> Moving : More Targets
    Waiting --> Idle : No Targets
    
    state Moving {
        [*] --> Up
        [*] --> Down
    }
    
    state Waiting {
        [*] --> DoorOpen
        DoorOpen --> DoorClosed : Timer
    }
```
