
"""The Environment class will manage the other objects in the environment"""
import multiprocessing as mp 
from functools import partial
class Environment:

    #list of rectangles in environment
    def __init__(self):
        self.bounding_boxes = []

    #iterator of the rects list
    def __iter__(self):
        i = 0
        while True:
            try:
                i %= len(self.bounding_boxes)
                yield self.bounding_boxes[i]
                i += 1
            except ZeroDivisionError:
                yield None


    #updates rects list
    def update(self, bounding_boxes):
        self.bounding_boxes = bounding_boxes

    #This is the functiont that the teams should call
    #safe_update handles all multiprocessing options
    #CAUTION: may not run only work on Linux/MacOS  
    def safe_update(self, bounding_boxes):
        pool = mp.Pool()
        m = mp.Manager()
        l = m.Lock()
        func = partial(self.update(bounding_boxes), l)
        pool.map(func, bounding_boxes)
        pool.close()
        pool.join()


  
