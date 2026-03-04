from enum import Enum
from entities.laser import laser
from entities.tracking_missile import tracking_missile
from typing import Union
class WeaponType(Enum):
    
    # Enum Members
    Laser = "laser"
    TrackingMissile = "Tracking missile"
    
    @classmethod
    def str_to_class(cls, s: str) -> Union[type[laser], type[tracking_missile]]:
        """Maps a string value to its corresponding entity class."""
        
        # We store the mapping inside the method so it doesn't 
        # accidentally become an Enum member.
        string_to_class_map = {
            cls.Laser.value: laser,
            cls.TrackingMissile.value: tracking_missile
        }
        
        if s in string_to_class_map:
            return string_to_class_map[s]
        else:
            # ValueError is the perfect exception when the input value is unrecognized
            raise ValueError(f"Unknown weapon type requested: '{s}'") 
            
    @staticmethod
    def tracking_missile_condition(score: int) -> bool:
        """Checks if the player score meets the threshold for the tracking missile."""
        return score >= 15000

if __name__ == "__main__":
    WeaponType.str_to_class(WeaponType.Laser.value)