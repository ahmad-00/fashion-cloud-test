from typing import List


class Mapping:
    def __init__(self, source_types: List[str], destination_type: str, source: str, destination: str):
        self.source_types = source_types
        self.destination_type = destination_type
        self.source = source
        self.destination = destination
        self.is_combined = len(source_types) > 1

