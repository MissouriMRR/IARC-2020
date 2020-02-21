from multiprocessing import Process, Value
from multiprocessing.managers import BaseManager

class Communication:

    x = 0
    y = 0

    # Use functions to access member variables of communication object
    # The object does not work properly when passed to a manager otherwise

    # Get member variable x to specified value
    def get_x(self):
        return self.x

    # Get member variable y to specified value
    def get_y(self):
        return self.y

    # Print x and y value
    def get(self):
        print(self.x,self.y)
    
    # Set member variable x to specified value
    def set_x(self,val):
        self.x = val

    # Set member variable y to specified value
    def set_y(self,val):
        self.y = val

    # Initialize x and y to one
    def __init__(self):
        self.x = 1
        self.y = 1

def flight(comm):
    comm.set_x(comm.get_x() + 1) 

def vision(comm):
    comm.set_y(comm.get_y() + 1)

def multi_proc():

    BaseManager.register('Communication',Communication)
    manager = BaseManager()
    manager.start()
    test = manager.Communication()

    # Create new processes
    print("-----Begin Processes-----")
    f = Process(target=flight, args=(test,))
    v = Process(target=vision, args=(test,))
   
    # Start flight and wait for it to finish 
    f.start()
    v.start()

    while(True):

        # If the process is no longer alive,
        # (i.e. error has been raised in this case)
        # then create a new instance and start the new process
        # (i.e. restart the process)
        if f.is_alive() == False:
            f = Process(target=flight, args=(test,))
            f.start()

        # Start vision and wait for it to finish 
        if v.is_alive() == False:
            v = Process(target=vision, args=(test,))
            v.start()

        test.get()
    
    f.join()
    v.join()

    print("----End of Processes----")

if __name__ == '__main__':
    multi_proc()
