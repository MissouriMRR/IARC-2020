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

### Times

1. Add a file to times/ named bench_*.py.

2. In this file create a class named Time*

- (Optional) Include a setup function that will run once before anything else.

- After setup is run, a dictionary named PARAMETERS should be in the class, {"benchmark_title": [parameters]}

3. When the benchmark is run, all methods in class named time_* will be run with [parameters].

4. Run time will be logged in the data frame.

### Accuracy

1. Add a file to accuracy/ named bench_*.py.

- Include a variable IMG_FOLDER = '', the folder in vision_images to use.

- This folder should include an Annotations folder from blob_annotator.

- This folder should include a benchmark.json file(see below).

2. In this file create a class named Accuracy*

- (Optional) Include a setup function that will run once before anything else.

3. When the benchmark is run, all methods in class named time_* will be run with [parameters] from benchmark.json.

4. Accuracy will be calculated based on classification setting in benchmark.json and logged.

#### benchmark.json

For the accuracy benchmarks

```json
 {
    "encoding": "color" | "depth" | "both",
    "classification": "location" | "in_frame",
    "types": {
        "side_view": "Module at a side view or close to it.",
        "bg_noise": "Module with lots of background noise."
    },
    "data": {
        "filename_1": "side_view",
        "filename_2": "bg_noise"
    }
}
```
