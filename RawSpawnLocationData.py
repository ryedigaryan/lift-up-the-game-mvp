class RawSpawnLocationData:
    def __init__(self, floor_number: int, x: int):
        """
        Holds raw data for a single spawn location.

        Args:
            floor_number (int): The floor number where this spawn location is.
            x (int): The x-coordinate of the spawn location.
        """
        self.floor_number = floor_number
        self.x = x
