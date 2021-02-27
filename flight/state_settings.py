"""Class to contain setters and getters for settings in various flight states"""

DEFAULT_EARLY_LAPS: int = 4


class StateSettings:
    def __init__(self):
        """Default constructor results in default settings"""
        self.do_early_laps: bool = True
        self.num_early_laps: int = DEFAULT_EARLY_LAPS
        self.go_to_mast: bool = True
        self.detect_module: bool = False

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
