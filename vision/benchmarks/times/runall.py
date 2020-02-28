"""
Run time benchmarks.
"""
import timeit
from times import modules


N_REPEATS = 100

if __name__ == '__main__':
    benchmarks = {}

    ## Find time benchmarks in modules
    for module in modules:
        for key, value in module.__dict__.items():
            if key[:4] == 'Time':
                benchmarks.update({key: value})

    ## Run benchmarks
    for b_name, benchmark in benchmarks.items():
        b_instance = benchmark()

        try:
            b_instance.setup()
        except AttributeError:
            print(f"No setup method found for {b_name}.")

        for m_name, method in benchmark.__dict__.items():
            if 'time_' not in m_name or not callable(method):
                continue
            
            try:
                time = timeit.timeit(lambda: method(b_instance), number=N_REPEATS) / N_REPEATS
            except Exception:
                print(f"{b_name}.{m_name}: error")
            else:
                print(f"{b_name}.{m_name}: {time:.5f}s")
