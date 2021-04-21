# Shared communication object between flight and vision code
class Communication:
    """
    Shared communication object between flight and vision code

    Attributes:
        state (str): name of the state in use
    Functions:
        __init__: default constructor for Communication class
        get_state: Returns the name of the current state
        set_state: Sets the name of the current state
    """
    def __init__(self):
        """
        Default constructor; initialize to start

        Parameters:
            N/A
        Return:
            None
        Logging:
            N/A
        """
        # Environment object to communicate with vision code
        # Shared state variable
        self.state: str = "start"

    # Use functions to access member variables of communication object
    # The object does not work properly when passed to a manager otherwise

    def get_state(self) -> str:
        """
        Get the current state

        Parameters:
            N/A
        Return:
            str: Name of the current state
        Logging:
            N/A
        """
        return self.state

    def set_state(self, new_state) -> None:
        """
        Set the member variable state to a new state

        Parameters:
            new_state (str): Name of the new state to be set
        Return:
            None
        Logging:
            N/A
        """
        self.state: str = new_state
