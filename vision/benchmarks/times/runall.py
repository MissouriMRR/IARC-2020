"""
Run time benchmarks.
"""
import timeit
import numpy as np
import pandas as pd

from times import modules


N_REPEATS = 5

if __name__ == '__main__':
    benchmarks = {}

    ## Find time benchmarks in modules
    for module in modules:
        for key, value in module.__dict__.items():
            if key[:4] == 'Time':
                benchmarks.update({key: value})

    ## Run benchmarks
    output = pd.DataFrame(columns=['class', 'method', 'test', 'time(s)'])

    for b_name, benchmark in benchmarks.items():
        b_instance = benchmark()

        try:
            b_instance.setup()
        except AttributeError:
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
                    print(f"{b_name}.{m_name}: error: {e}")

                    output.loc[len(output)] = [b_name, m_name, p_name, np.nan]
                else:
                    print(f"{b_name}.{m_name}: {p_name} {time:.5f}s")

                    output.loc[len(output)] = [b_name, m_name, p_name, time]

    #print(output.head(15))
    # output.to_csv('', index=False)

    print()
