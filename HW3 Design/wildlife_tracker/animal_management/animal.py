from typing import Any, Optional

class Animal:

    #pass
    def __init__(self,
                animal_id: int,
                health_status: Optional[str] = None,
                age: Optional[int] = None) -> None:
        self.animal_id = animal_id
        self.health_status = health_status
        self.age = age

    # def get_animal_by_id(animal_id: int) -> Optional[Animal]:
    #     pass

    def get_animal_details(animal_id) -> dict[str, Any]:
        pass

    def update_animal_details(animal_id: int, **kwargs: Any) -> None:
        pass