"""
Run time benchmarks.

Results: (found, missed, extra)

Process
-------
files = [filename for filename in 'times/' if 'bench' in filename]
benchmarks = [class for class in filenames if 'Accuracy' in class_name]

for benchmark in benchmarks:
    instance = benchmark()

    try: instance.setup()

    for method in benchmark if 'accuracy' in method_name:
        for title, parameters in benchmark.PARAMETERS.items():
            accuracy(method(instance, *parameters))

            log(benchmark, method, title, accuracy)

Suggested Parameter Defaults
----------------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
"""
import os
import sys
import json
import numpy as np
import pandas as pd

import common
from accuracy import modules


def accuracy_boundingbox(data, annotation, method, instance):  ## NOT IMPLEMENTED
    """
    Calculate how far off each bounding box was

    Parameters
    ----------
    data: color_image, depth_image

    annotation: pascal voc annotation

    method: function(instance, *data)

    instance: instance of object

    Returns
    -------
    (int, int, int) boxes_found, boxes_missed, boxes_extra.
    """
    FOUND_THRESHOLD = 5  # pixels

    ##
    bounding_boxes = method(instance, *data)

    ##
    boxes_found, boxes_missed, boxes_extra = 0, 0, 0

    for value in annotation.findall('object'):
        annotation_bounding_box = value.find('bndbox')

        ax1, ay1, ax2, ay2 = [int(annotation_bounding_box.find(param).text) for param in ['xmin', 'ymin', 'xmax', 'ymax']]

        for bounding_box in bounding_boxes:
            X, Y, Z = [], [], []
            for x, y in bounding_box.vertices:
                X.append(x)
                Y.append(y)

            X, Y = np.unique(X), np.unique(Y)
            bx1, by1, bx2, by2 = min(X), min(Y), max(X), max(Y)

            ##
            x1_close = bx1 - THRESHOLD <= ax1 <= bx1 + THRESHOLD
            y1_close = by1 - THRESHOLD <= ay1 <= by1 + THRESHOLD
            x2_close = bx2 - THRESHOLD <= ax2 <= bx2 + THRESHOLD
            y2_close = by2 - THRESHOLD <= ay2 <= by2 + THRESHOLD

            if all((x1_close, y1_close, x2_close, y2_close)):
                boxes_found += 1

    boxes_missed = len(annotation.findall('object')) - boxes_found
    boxes_extra = len(bounding_boxes) - boxes_found

    return boxes_found, boxes_missed, boxes_extra


def accuracy_boolean(data, annotation, method, instance):
    """
    Determine whether method output is correct.

    Parameters
    ----------
    data: color_image, depth_image
    annotation: Annotation from blob_annotator
    method: function[instance, data] -> BoundingBox
    instance: instance of benchmark

    Returns
    -------
    found, missed, extra
    """
    ## Prediction
    bounding_boxes = method(instance, *data)

    prediction = bool(len(bounding_boxes))

    ## Expected
    expected = bool(len(annotation.findall('object')))

    ## Calculate accuracy
    found = int(prediction == expected)
    missed = 1 - found
    extra = 0

    return found, missed, extra


classification_map = {
    'location': accuracy_boundingbox,
    'in_frame': accuracy_boolean,
}

if __name__ == '__main__':
    benchmarks = {}

    ## Command line args
    keyword = sys.argv[1] if len(sys.argv) > 1 else ''

    ## Find time benchmarks in modules
    for module in modules:
        for key, value in module.__dict__.items():
            if 'Accuracy' in key and keyword.lower() in key.lower():
                benchmarks.update({key: value})

        ## Read benchmark configuration
        with open(os.path.join('..', 'vision_images', module.__dict__['IMG_FOLDER'], 'benchmark.json')) as file:
            benchmark_config = json.load(file)

        classification = benchmark_config['classification']
        classification_method = classification_map[classification]

        encoding = benchmark_config['encoding']
        types = benchmark_config['types']
        parameters = benchmark_config['data']

        ## Load annotations
        path = os.path.join('..', 'vision_images', module.__dict__['IMG_FOLDER'])

        annotations = common.read_annotations(path)

        ## Run benchmarks
        output = pd.DataFrame(columns=['class', 'method', 'type', 'filename', 'found', 'missed', 'extra'])

        for b_name, benchmark in benchmarks.items():
            b_instance = benchmark()

            try:
                b_instance.setup()
            except AttributeError as e:
                print(f"No setup method found for {b_name}.")

            for m_name, method in benchmark.__dict__.items():
                if 'accuracy_' not in m_name or not callable(method):
                    continue

                for filename, p_type in parameters.items():
                    try:
                        images = common.read_image(os.path.join(path, filename), encoding)

                        annotation = annotations[filename.split('.')[0].split('\\')[-1].split('/')[-1]]

                        result = classification_method(images, annotation, method, b_instance)

                    except Exception as e:
                        print(f"{b_name}.{m_name}: {filename} error: {e}")

                        output.loc[len(output)] = [b_name, m_name, p_type, filename, np.nan]
                    else:
                        print(f"{b_name}.{m_name}: {filename} {result}")

                        output.loc[len(output)] = [b_name, m_name, p_type, filename, *result]

    # print(output.head(15))
    # output.to_csv('', index=False)

    print()
