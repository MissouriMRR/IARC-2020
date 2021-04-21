class FailureFlags:
    """
    Abstract class used by the pipeline to track which algorithm failed
    in the event of the program crashing

    For each attribute, a value of True signals that the algorithm
    ran to completion without any problems
    """

    def __init__(self):
        pass

    def __str__(self):
        return "INVALID STATE"


class ObstacleDetectionFlags(FailureFlags):
    """
    Class used by the pipeline to track which algorithm failed
    in the event of the program crashing during obstacle detection ("early_laps")
    """

    def __init__(self):
        self.obstacle_finder = True
        self.obstacle_tracker = True

    def __str__(self):
        return (
            "obstacle_finder: "
            + ("OK" if self.obstacle_finder else "ERROR")
            + ", obstacle_tracker: "
            + ("OK" if self.obstacle_tracker else "ERROR")
        )


class TextDetectionFlags(FailureFlags):
    """
    Class used by the pipeline to track which algorithm failed
    in the event of the program crashing during text detection
    """

    def __init__(self):
        self.detect_russian_word = True

    def __str__(self):
        return "detect_russian_word: " + ("OK" if self.detect_russian_word else "ERROR")


class ModuleDetectionFlags(FailureFlags):
    """
    Class used by the pipeline to track which algorithm failed
    in the event of the program crashing during module detection
    """

    def __init__(self):
        self.set_img = True
        self.detect_russian_word = True
        self.set_text = True
        self.is_in_frame = True
        self.get_center = True
        self.get_module_depth = True
        self.region_of_interest = True
        self.get_module_orientation = True
        self.get_module_bounds = True
        self.get_module_roll = True

    def __str__(self):
        return (
            "setImg: "
            + ("OK" if self.set_img else "ERROR")
            + ", detect_russian_word: "
            + ("OK" if self.detect_russian_word else "ERROR")
            + ", set_text: "
            + ("OK" if self.set_text else "ERROR")
            + ", is_in_frame: "
            + ("OK" if self.is_in_frame else "ERROR")
            + ", get_center: "
            + ("OK" if self.get_center else "ERROR")
            + ", get_module_depth: "
            + ("OK" if self.get_module_depth else "ERROR")
            + ", region_of_interest: "
            + ("OK" if self.region_of_interest else "ERROR")
            + ", get_module_orientation: "
            + ("OK" if self.get_module_orientation else "ERROR")
            + ", get_module_bounds: "
            + ("OK" if self.get_module_bounds else "ERROR")
            + ", get_module_roll: "
            + ("OK" if self.get_module_roll else "ERROR")
        )
