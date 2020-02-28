# Shared communication object between flight and vision code
class Communication:
    # Default constructor
    # Initialize State to start
    def __init__(self):
        # Environment object to communicate with vision code
        # Shared state variable
        self.state: str = "start"

    # Use functions to access member variables of communication object
    # The object does not work properly when passed to a manager otherwise

    # Get the current state
    def get_state(self):
        return self.state

    # Set member variable state to new state
    def set_state(self, new_state):
        self.state: str = new_state
