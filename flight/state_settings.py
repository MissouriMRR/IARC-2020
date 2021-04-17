"""Class to contain setters and getters for settings in various flight states"""

DEFAULT_EARLY_LAPS: int = 2
DEFAULT_RETURN_LAPS: int = 2
DEFAULT_VISION_TEST: str = "module"
DEFAULT_RUN_TITLE: str = "N/A"
DEFAULT_RUN_DESCRIPTION: str = "N/A"


class StateSettings:
    def __init__(self):
        """Default constructor results in default settings"""

        # Takeoff settings
        self.simple_takeoff: bool = False

        # EarlyLaps settings
        self.do_early_laps: bool = True
        self.num_early_laps: int = DEFAULT_EARLY_LAPS

        # ToMast settings
        self.go_to_mast: bool = True

        # DetectModule settings
        self.detect_module: bool = False
        self.detect_mast_text: bool = False
        self.vision_test_type: str = DEFAULT_VISION_TEST

        # ReturnLaps settings
        self.do_return_laps: bool = False
        self.num_return_laps: int = DEFAULT_RETURN_LAPS

        # Other settings
        self.run_title: str = DEFAULT_RUN_TITLE
        self.run_description: str = DEFAULT_RUN_DESCRIPTION

    # ---- Takeoff settings ---- #

    def enable_simple_takeoff(self, simple_takeoff: bool) -> None:
        """
        Setter for whether to perform simple takeoff instead of regular takeoff
            simple_takeoff(bool): True for drone to go straight up, False to behave normally
        """
        self.simple_takeoff = simple_takeoff

    # ---- EarlyLaps settings ---- #

    def enable_early_laps(self, do_early_laps: bool) -> None:
        """Setter for whether to do early laps"""
        self.do_early_laps = do_early_laps

    def set_number_of_early_laps(self, num_laps: int) -> None:
        """Setter for how many early laps to do"""
        self.num_early_laps = num_laps

    # ---- ToMast settings ---- #

    def enable_to_mast(self, go_to_mast: bool) -> None:
        """Setter for whether to go to the mast"""
        self.go_to_mast = go_to_mast

    # ---- DetectModule settings ---- #

    def enable_module_detection(self, detect_module: bool) -> None:
        """Setter for whether to detect the module"""
        self.detect_module = detect_module

    def enable_text_detection(self, detect_text: bool) -> None:
        """Setter for whether to detect the mast text"""
        self.detect_mast_text = detect_text

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

    # ---- ReturnLaps settings ---- #

    def enable_return_laps(self, do_return_laps: bool) -> None:
        """Setter for whether to do return laps"""
        self.do_return_laps = do_return_laps

    def set_number_of_return_laps(self, num_laps: int) -> None:
        """Setter for how many return laps to do"""
        self.num_return_laps = num_laps

    # ---- Other settings ---- #

    def set_run_title(self, title: str) -> None:
        """Set a title for the run/test to be output in logging"""
        self.run_title = title

    def set_run_description(self, description: str) -> None:
        """Set a description for the run/test to be output in logging"""
        self.run_description = description
