#!/usr/bin/env python3

from multiprocessing import Process
from multiprocessing.managers import BaseManager

# Shared communication object between flight and vision code
class Communication:

    # Default constructor
    # Initialize x and y to one
    def __init__(self):
        # Arbitrary data values
        self.x = 1
        self.y = 1

    # Use functions to access member variables of communication object
    # The object does not work properly when passed to a manager otherwise

    # Get member variable x to specified value
    def get_x(self):
        return self.x

    # Get member variable y to specified value
    def get_y(self):
        return self.y

    # Print x and y values
    def get(self):
        print(self.x, self.y)

    # Set member variable x to specified value
    def set_x(self, val):
        self.x = val

    # Set member variable y to specified value
    def set_y(self, val):
        self.y = val


# Arbitrary flight function with communication object
# paramter
def flight(comm):
    comm.set_x(comm.get_x() + 1)


# Arbitrary vision function with communication object
# paramter
def vision(comm):
    comm.set_y(comm.get_y() + 1)


def main():

    # Register Communication object to Base Manager
    BaseManager.register("Communication", Communication)
    # Create manager object
    manager = BaseManager()
    # Start manager
    manager.start()
    # Create Communication object from manager
    test = manager.Communication()

    # Create new processes
    print("-----Begin Processes-----")
    f = Process(target=flight, args=(test,))
    v = Process(target=vision, args=(test,))

    # Start flight and vision functions
    f.start()
    v.start()

    while True:

        # If the process is no longer alive,
        # (i.e. error has been raised in this case)
        # then create a new instance and start the new process
        # (i.e. restart the process)
        if f.is_alive() == False:
            f = Process(target=flight, args=(test,))
            f.start()

        # Start vision if it is no longer running
        # Same idea as above code for flight
        if v.is_alive() == False:
            v = Process(target=vision, args=(test,))
            v.start()

        test.get()

    # Join flight and vision processes before exiting function
    f.join()
    v.join()

    print("----End of Processes----")


if __name__ == "__main__":
    # Run multiprocessing function
    main()
