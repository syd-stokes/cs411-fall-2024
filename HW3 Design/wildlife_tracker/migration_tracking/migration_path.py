from typing import Optional

from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:

    #pass

    def __init__(self,
                species: str,
                start_location: int,
                destination: int,  
                duration: Optional[int] = None) -> None:
        self.start_location = start_location
        self.destination = destination
        self.duration = duration
        self.species = species

    def remove_migration_path(path_id: int) -> None:
        pass

    def create_migration_path(species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None) -> None:
        pass

    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass