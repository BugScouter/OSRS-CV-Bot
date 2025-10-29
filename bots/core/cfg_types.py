import random
import json
from typing import List, Tuple, Dict, Any, Union
class RGBParam:
    def __init__(self, r: int, g: int, b: int):
        # Validate RGB values are in valid range
        if not all(0 <= val <= 255 for val in [r, g, b]):
            raise ValueError("RGB values must be between 0 and 255")
        self._r = r
        self._g = g
        self._b = b

    @staticmethod
    def type() -> str:
        return "RGB"

    @property
    def value(self) -> Tuple[int, int, int]:
        """Get RGB values as a tuple"""
        return (self._r, self._g, self._b)
    
    @property
    def r(self) -> int:
        """Get red value"""
        return self._r
    
    @property
    def g(self) -> int:
        """Get green value"""
        return self._g
    
    @property
    def b(self) -> int:
        """Get blue value"""
        return self._b
    
    def to_hex(self) -> str:
        """Export RGB as hex string (e.g., '#FF0000')"""
        return "#{:02X}{:02X}{:02X}".format(self._r, self._g, self._b)
    
    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Export RGB as tuple"""  
        return self.value
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> 'RGBParam':
        """Create RGBParam from RGB values"""
        return cls(r, g, b)
    
    @classmethod  
    def from_tuple(cls, rgb_tuple: Tuple[int, int, int]) -> 'RGBParam':
        """Create RGBParam from RGB tuple"""
        if len(rgb_tuple) != 3:
            raise ValueError("RGB tuple must contain exactly 3 values")
        return cls(*rgb_tuple)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'RGBParam':
        """Create RGBParam from hex string (e.g., '#FF0000' or 'FF0000')"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters long")
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return cls(r, g, b)
        except ValueError as e:
            raise ValueError(f"Invalid hex color format: {hex_color}") from e
    
    @staticmethod
    def load(value) -> 'RGBParam':
        """Load RGBParam from various input formats"""
        if isinstance(value, list) and len(value) == 3:
            # List of integers [r, g, b]
            return RGBParam.from_tuple(tuple(value))
        elif isinstance(value, tuple) and len(value) == 3:
            # Tuple of integers (r, g, b)
            return RGBParam.from_tuple(value)
        elif isinstance(value, str):
            # Hex string '#FF0000' or 'FF0000'
            return RGBParam.from_hex(value)
        else:
            raise ValueError("RGB value must be a list/tuple of three integers or a hex string")

    def __repr__(self):
        return f"RGBParam({self._r}, {self._g}, {self._b})"
    
    def __eq__(self, other):
        if isinstance(other, RGBParam):
            return self.value == other.value
        elif isinstance(other, tuple) and len(other) == 3:
            return self.value == other
        return False
    
    def __iter__(self):
        """Allow unpacking like a tuple: r, g, b = rgb_param"""
        return iter(self.value)
    
    def __getitem__(self, index):
        """Allow indexing like a tuple: rgb_param[0] for red"""
        return self.value[index]
    
    def __len__(self):
        """Allow len() to work like a tuple"""
        return 3
    
    def to_json(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict"""
        return {
            "type": self.type(),
            "value": {
                "rgb": self.to_rgb_tuple(),
                "hex": self.to_hex()
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'RGBParam':
        """Import from JSON data"""
        if data.get("type") != cls.type():
            raise ValueError(f"Expected type '{cls.type()}', got '{data.get('type')}'")
        
        value = data["value"]
        # Try to load from hex first, then from rgb tuple
        if isinstance(value, dict):
            if "hex" in value:
                return cls.from_hex(value["hex"])
            elif "rgb" in value:
                return cls.from_tuple(tuple(value["rgb"]))
        
        # Fallback to the existing load method
        return cls.load(value)
    
class RangeParam:
    def __init__(self, min_value: float, max_value: float):
        self.min_value = min_value
        self.max_value = max_value

    @staticmethod
    def type() -> str:
        return "Range"
    
    @property
    def value(self) -> Tuple[float, float]:
        return (self.min_value, self.max_value)
    
    @staticmethod
    def load(value: List[float]) -> 'RangeParam':
        if len(value) != 2:
            raise ValueError("Range value must be a list of two floats.")
        return RangeParam(value[0], value[1])
    
    def choose(self) -> float:
        """Randomly choose a value within the range [min_value, max_value]."""
        return random.uniform(self.min_value, self.max_value)
    
    def to_json(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict"""
        return {
            "type": self.type(),
            "value": [self.min_value, self.max_value]
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'RangeParam':
        """Import from JSON data"""
        if data.get("type") != cls.type():
            raise ValueError(f"Expected type '{cls.type()}', got '{data.get('type')}'")
        return cls.load(data["value"])
    
    def __repr__(self):
        return f"RangeValue({self.min_value}, {self.max_value})"


class BreakCfgParam:
    def __init__(self, break_duration: RangeParam, break_chance):
        """
        break_duration: RangeParam
        break_chance: float or FloatParam (legacy). Stored internally as float.
        """
        self.break_duration = break_duration
        # accept either raw float or FloatParam for backward compatibility
        if hasattr(break_chance, "value"):
            self.break_chance = float(getattr(break_chance, "value"))
        else:
            self.break_chance = float(break_chance)
    
    @property
    def value(self):
        return self.break_duration.value, self.break_chance
    
    @staticmethod
    def type() -> str:
        return "BreakCfg"
    
    @staticmethod
    def load(value: List) -> 'BreakCfgParam':
        if len(value) != 2:
            raise ValueError("BreakCfg value must be a list of two elements: [break_duration, break_chance].")
        
        break_duration = RangeParam.load(value[0])
        # accept raw float from config
        try:
            break_chance = float(value[1])
        except Exception as e:
            raise ValueError(f"BreakCfg break_chance must be a float: {e}") from e
        
        return BreakCfgParam(break_duration, break_chance)
    
    def should_break(self) -> bool:
        """Decides whether to take a break based on the configured chance."""
        return random.random() < float(self.break_chance)
    
    def to_json(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict"""
        return {
            "type": self.type(),
            "value": {
                "break_duration": self.break_duration.to_json(),
                "break_chance": self.break_chance
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'BreakCfgParam':
        """Import from JSON data"""
        if data.get("type") != cls.type():
            raise ValueError(f"Expected type '{cls.type()}', got '{data.get('type')}'")
        
        value = data["value"]
        if isinstance(value, dict):
            break_duration = RangeParam.from_json(value["break_duration"])
            break_chance = value["break_chance"]
            return cls(break_duration, break_chance)
        else:
            # Fallback to existing load method
            return cls.load(value)
    
    def __repr__(self):
        return f"BreakCfgValue({self.break_duration}, {self.break_chance})"
    
class WaypointParam:
    """
    Represents a waypoint with x, y, and optional z coordinates.
    Tolerance is the allowed deviation from the exact coordinates.
    """
    
    def __init__(self, x: int, y: int, z: int, chunk: int, tolerance: int = 5):
        self.x = x
        self.y = y
        self.z = z
        self.chunk = chunk
        self.tolerance = tolerance

    @staticmethod
    def type() -> str:
        return "Waypoint"

    @property
    def value(self):
        return [(self.x, self.y, self.z), self.chunk, self.tolerance]
    
    def gen_tile(self, color: RGBParam) -> dict:
        # [{"regionId":12853,"regionX":58,"regionY":36,"z":0,"color":"#FF00FFFF"}]
        return {
            "regionId": self.chunk,
            "regionX": self.x,
            "regionY": self.y,
            "z": self.z,
            "color": color.to_hex()
        }
    
    

    
    @staticmethod
    def load(value: list) -> 'WaypointParam':
        """
        Parses a waypoint value and returns a WaypointParam instance.
        Supported formats:
        - [[x, y, z], chunk, tolerance]
        - [x, y, z, chunk]
        - [[x, y, z], chunk]
        """
        # Default tolerance
        tolerance = 5
        
        # Handle format [[x, y, z], chunk, tolerance] or [[x, y, z], chunk]
        if isinstance(value[0], list):
            coords = value[0]
            if len(coords) != 3:
                raise ValueError("Waypoint coordinates must include x, y, and z values.")
            
            if len(value) < 2:
                raise ValueError("Waypoint must include chunk value.")
            
            chunk = value[1]
            if len(value) > 2:
                tolerance = value[2]
            
            return WaypointParam(coords[0], coords[1], coords[2], chunk, tolerance)
        
        # Handle format [x, y, z, chunk]
        elif len(value) == 4:
            x, y, z, chunk = value
            return WaypointParam(x, y, z, chunk, tolerance)
        
        else:
            raise ValueError("Invalid waypoint format. Must provide x, y, z, and chunk values.")

    def to_json(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict"""
        return {
            "type": self.type(),
            "value": {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "chunk": self.chunk,
                "tolerance": self.tolerance
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'WaypointParam':
        """Import from JSON data"""
        if data.get("type") != cls.type():
            raise ValueError(f"Expected type '{cls.type()}', got '{data.get('type')}'")
        
        value = data["value"]
        if isinstance(value, dict):
            return cls(
                value["x"], value["y"], value["z"],
                value["chunk"], value.get("tolerance", 5)
            )
        else:
            # Fallback to existing load method
            return cls.load(value)
    
    def __repr__(self):
        return f"WaypointValue({self.x}, {self.y}, {self.z})"
    
class RouteParam:
    def __init__(self, waypoints: List[WaypointParam]):
        self.waypoints = waypoints

    @staticmethod
    def type() -> str:
        return "Route"
    
    @property
    def value(self) -> List[List[int]]:
        return [wp.value for wp in self.waypoints]
    
    def reverse(self) -> 'RouteParam':
        """Returns a new RouteParam with waypoints in reverse order."""
        return RouteParam(self.waypoints[::-1])

    @staticmethod
    def load(value: List[List[int]]) -> 'RouteParam':
        waypoints = [WaypointParam.load(wp) for wp in value]
        return RouteParam(waypoints)

    def to_json(self) -> Dict[str, Any]:
        """Export as JSON-serializable dict"""
        return {
            "type": self.type(),
            "value": [wp.to_json() for wp in self.waypoints]
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'RouteParam':
        """Import from JSON data"""
        if data.get("type") != cls.type():
            raise ValueError(f"Expected type '{cls.type()}', got '{data.get('type')}'")
        
        waypoints = []
        for wp_data in data["value"]:
            if isinstance(wp_data, dict) and wp_data.get("type") == "Waypoint":
                waypoints.append(WaypointParam.from_json(wp_data))
            else:
                waypoints.append(WaypointParam.load(wp_data))
        
        return cls(waypoints)
    
    def __repr__(self):
        return f"RouteValue({self.waypoints})"
    

TYPES = [RGBParam, WaypointParam, RouteParam]