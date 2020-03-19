"""
Run time benchmarks.

    python times/runall.py module
will only run benchmarks w/ module in name.


Process
-------
files = [filename for filename in 'times/' if 'bench' in filename]
benchmarks = [class for class in filenames if 'Time' in class_name]

for benchmark in benchmarks:
    instance = benchmark()

    try: instance.setup()

    if not hasattr(benchmark, 'PARAMETERS'):
        benchmark.PARAMETERS = {'': []}

    for method in benchmark if 'time' in method_name:
        for title, parameters in benchmark.PARAMETERS.items():
            time(method(instance, *parameters))

            log(benchmark, method, title, time)

Suggested Parameter Defaults
----------------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
"""
import __init__

import sys
import timeit
import numpy as np
import pandas as pd

from times import modules


N_REPEATS = 1

if __name__ == '__main__':
    benchmarks = {}

    ## Command line args
    keyword = sys.argv[1] if len(sys.argv) > 1 else ''

    ## Find time benchmarks in modules
    for module in modules:
        for key, value in module.__dict__.items():
            if key[:4] == 'Time' and keyword.lower() in key.lower():
                benchmarks.update({key: value})

    ## Run benchmarks
    output = pd.DataFrame(columns=['class', 'method', 'test', 'time(s)'])

    for b_name, benchmark in benchmarks.items():
        b_instance = benchmark()

        try:
            b_instance.setup()
        except AttributeError as e:
            print(f"No setup method found for {b_name}.")

        if not hasattr(b_instance, 'PARAMETERS'):
            b_instance.PARAMETERS = {'': []}

        for m_name, method in benchmark.__dict__.items():
            if 'time_' not in m_name or not callable(method):
                continue

            for p_name, parameters in b_instance.PARAMETERS.items():
                try:
                    time = timeit.timeit(lambda: method(b_instance, *parameters), number=N_REPEATS) / N_REPEATS
                except Exception as e:
                    print(f"{b_name}.{m_name}: {p_name} error: {e}")

                    output.loc[len(output)] = [b_name, m_name, p_name, np.nan]
                else:
                    print(f"{b_name}.{m_name}: {p_name} {time:.5f}s")

                    output.loc[len(output)] = [b_name, m_name, p_name, time]

    #print(output.head(15))
    # output.to_csv('', index=False)

    print()
