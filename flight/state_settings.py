"""Class to contain setters and getters for settings in various flight states"""

DEFAULT_EARLY_LAPS: int = 2


class StateSettings:
    def __init__(self):
        """Default constructor results in default settings"""
        self.do_early_laps: bool = True
        self.num_early_laps: int = DEFAULT_EARLY_LAPS
        self.go_to_mast: bool = True
        self.detect_module: bool = False
        self.simple_takeoff: bool = False
        self.vision_test_type: str = "module"

    def set_early_laps(self, do_early_laps: bool) -> None:
        """Setter for whether to do early laps"""
        self.do_early_laps = do_early_laps

    def set_number_of_early_laps(self, num_laps: int) -> None:
        """Setter for how many early laps to do"""
        self.num_early_laps = num_laps

    def set_to_mast(self, go_to_mast: bool) -> None:
        """Setter for whether to go to the mast"""
        self.go_to_mast = go_to_mast

    def set_detect_module(self, detect_module: bool) -> None:
        """Setter for whether to detect the module"""
        self.detect_module = detect_module

    def enable_simple_takeoff(self, simple_takeoff: bool) -> None:
        """
        Setter for whether to perform simple takeoff instead of regular takeoff
            simple_takeoff(bool): True for drone to go straight up, False to behave normally
        """
        self.simple_takeoff = simple_takeoff

    def set_vision_test(self, test_type: str) -> None:
        """
        Setter for the type of vision test to run
        This should only generally only be used with simple takeoff
            test_type(str) 'module' for module detection or 'text' for mast text detection
        """
        if test_type == "module" or test_type == "text":
            self.vision_test_type = test_type
        else:
            raise ValueError(f"test_type must be 'module' or 'text', got {test_type}")
