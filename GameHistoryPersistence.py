import csv
import os
from typing import List
from RawGameHistoryEntry import RawGameHistoryEntry


class GameHistoryPersistence:
    def __init__(self, output_path: str):
        """
        Handles reading and writing game history data.

        Args:
            output_path (str): The directory where the history file is stored.
        """
        self.file_path = os.path.join(output_path, "game_history.csv")
        self.fieldnames = ["timestamp_epoch_seconds", "level", "penalty"]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Creates the CSV file with a header if it doesn't exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def read_all(self) -> List[RawGameHistoryEntry]:
        """
        Reads all history entries from the CSV file.

        Returns:
            List[RawGameHistoryEntry]: A list of all history entries.
        """
        history = []
        with open(self.file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                history.append(RawGameHistoryEntry(
                    timestamp_epoch_seconds=int(row['timestamp_epoch_seconds']),
                    level=row['level'],
                    penalty=float(row['penalty'])
                ))
        return history

    def append(self, history_entry: RawGameHistoryEntry):
        """
        Appends a new history entry to the CSV file.

        Args:
            history_entry (RawGameHistoryEntry): The new entry to add.
        """
        with open(self.file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow({
                "timestamp_epoch_seconds": history_entry.timestamp_epoch_seconds,
                "level": history_entry.level,
                "penalty": history_entry.penalty
            })
