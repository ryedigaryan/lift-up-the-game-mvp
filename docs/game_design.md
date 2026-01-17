# Lift Up Game - Design Document

## 1. Game Overview
**Lift Up** is a simulation/strategy game where the player manages a set of elevators (lifts) to transport customers between floors efficiently. The goal is to minimize the total penalty score, which increases based on customer wait times and travel times.

## 2. Core Mechanics

### 2.1. The Building
*   **Floors**: The game consists of a fixed number of floors (currently 5).
*   **Lifts**: There are two lifts ("A" and "B") that travel vertically between floors.
*   **Spawning**: Customers spawn randomly at designated locations on each floor.

### 2.2. Customers
Customers appear on floors and request transport to a different floor.
*   **States**:
    *   `waiting_for_lift_selection`: Wandering on the floor, waiting for the player to assign a lift.
    *   `walking_to_lift`: Moving towards the assigned lift.
    *   `waiting_at_lift`: Standing at the lift door, waiting for it to arrive/open.
    *   `in_lift`: Inside the lift, traveling to the destination.
    *   `exiting_lift`: Walking away from the lift at the destination floor.
    *   `delivered`: Reached the destination spawn point (despawned).
*   **Attributes**:
    *   **Target Floor**: The floor the customer wants to go to.
    *   **Priority**: Customers can be "High Priority" (Triangle) or "Normal Priority" (Rectangle).
    *   **Color**: Randomly assigned bright color.
    *   **Wandering**: Customers wander slightly left/right while waiting.

### 2.3. Player Interaction
*   **Selection**: The player clicks on a customer's request popup to assign a lift.
*   **Assignment**: The player chooses either Lift A or Lift B for the customer.
*   **Feedback**:
    *   **Request Popup**: Shows target floor, current wait time, and running penalty.
    *   **Info Popup**: Shows tracking info for assigned customers.
    *   **Delivered Popup**: Shows final stats upon delivery.

### 2.4. Scoring (Penalty System)
The game uses a penalty system where lower is better. Penalty is calculated as:
`Penalty = ((AssignmentTime - RequestTime) * APC + (DeliveryTime - AssignmentTime) * DPC) * CIPC`

*   **APC (Assignment Penalty Coefficient)**: Weight for time spent waiting for assignment.
*   **DPC (Delivery Penalty Coefficient)**: Weight for time spent traveling/waiting for lift.
*   **CIPC (Customer Importance Penalty Coefficient)**: Multiplier based on customer priority.

| Priority | APC | DPC | CIPC | Shape |
| :--- | :---: | :---: | :---: | :---: |
| Normal | 1 | 2 | 1 | Rectangle |
| High | 3 | 4 | 2 | Triangle |

## 3. Lift Logic (AI)

The lifts operate using a standard **SCAN (Elevator) Algorithm** to efficiently service requests.

### 3.1. Pathfinding
1.  **Request Collection**: The lift gathers all pickup requests (from player) and delivery requests (from passengers).
2.  **Partitioning**: Stops are divided into `up_stops` (floors >= current) and `down_stops` (floors < current).
3.  **Sequence Generation**:
    *   If moving **UP**: Service all `up_stops` (ascending), then all `down_stops` (descending).
    *   If moving **DOWN**: Service all `down_stops` (descending), then all `up_stops` (ascending).
4.  **Idle Behavior**: If idle, the lift sets its initial direction towards the closest request.

### 3.2. Door & Boarding Logic
*   **Arrival**: When arriving at a floor, the lift opens doors (`waiting` state).
*   **Exchange**: Passengers for this floor exit first. Then, waiting customers board.
*   **Polite Waiting**:
    *   If a new customer is assigned to a lift *while* it is waiting at that floor, the door timer resets.
    *   If a customer boards the lift, the door timer resets.
*   **Departure**: After the `door_wait_time` (2.0s) expires without new activity, the doors close and the lift moves to the next target.
