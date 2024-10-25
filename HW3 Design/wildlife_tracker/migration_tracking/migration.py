from typing import Any, Optional

from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:

    def __init__(self,
                migration_id: int, 
                start_location: int, 
                current_date: str,
                destination: int, 
                current_location: str,
                start_date: str, 
                species,
                migration_path: MigrationPath,
                status: str = "Scheduled", 
                duration: Optional[int] = None
                ) -> None:
        self.migration_id = migration_id
        self.start_location = start_location
        self.species = species
        self.destination = destination
        self.start_date = start_date
        self.status = status
        self.duration = duration
        self.current_date = current_date
        self.current_location = current_location
        self.migration_path = migration_path

    def get_migration_details(self) -> dict[str, Any]:
        pass

    def update_migration_details(self, **kwargs: Any) -> None:
        pass