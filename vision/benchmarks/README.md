# Vision Benchmarks

Time and accuracy benchmarks for the algorithms in vision/.

## Running

Starting in the benchmarks directory, run

```bash
    python3 accuracy/runall.py

    or

    python3 times/runall.py
```

## Contributing

See the runall of the benchmark type for requirements.
Use an existing file as a baseline.

### Times

1. Add a file to times/ named bench_*.py.

2. In this file include a class named Time*

 - In this method you may optionally include a setup function
   that will be run before anything else.

 - After setup there should be a dictionary named PARAMETERS in the class.
  {'title': [parameters], ...}

  - Every function in the class named time_* will be timed using these parameters and logged with the given title.

### Accuracy

1. Add file to accuracy/ named bench_*.py

2. In this file include a class named Accuracy*

- FOLDER

3. There must be a file named vision_images/FOLDER/benchmark.json

- This file must be configured as follows

```json
 {
    "encoding": "color" or "depth" or "both"
    "classification": "location" or "in_frame" or ....,
    "types": {
        "example_one": "These are images that have lots of background nosie with the module in them.",
        "example_two": "These are images that have lots of background nosie without the module in them."
    },
    "data": {
        "filename_1": "example_one",
        "filename_2": "example_two"
    }
}
```

4. Each function in the class named accuracy_* will be run with each image in data.
