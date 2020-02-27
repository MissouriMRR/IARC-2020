"""
Import all classes via __init__.py

For each class, 
 for time_ method in class:
     run class.setup()
     
     run timeit.timeit(lambda: class.time_...(), number=5) / 5
"""
from times import modules


if __name__ == '__main__':
    benchmarks = {}

    for module in modules:
        #print(benchmark.__dict__)

        for key, value in module.__dict__.items():
            if key[:4] == 'Time':
                benchmarks.update({key: value})

    for key, benchmark in benchmarks.items():
        print(key, benchmark)
