class RawGameHistoryEntry:
    def __init__(self, timestamp_epoch_seconds: int, level: str, penalty: float):
        """
        Holds raw data for a single game history entry.

        Args:
            timestamp_epoch_seconds (int): The time the game was completed, as a Unix timestamp.
            level (str): The name of the level that was played (e.g., "level_1").
            penalty (float): The final penalty score for the game.
        """
        self.timestamp_epoch_seconds = timestamp_epoch_seconds
        self.level = level
        self.penalty = penalty
