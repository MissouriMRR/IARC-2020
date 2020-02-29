"""
Common functions for benchmarks to make use of.

NOTE: Do no edit, only append!
"""
import os
import lxml
import numpy as np
import cv2


def read_image(path, encoding):
    """
    Read image according to encoding.

    Parameters
    ----------
    path: str
        Location of depth or color image.
    encoding: color, depth or both
        How is image data stored.

    Returns
    -------
    [color_image, depth_image]
    """
    if encoding == 'color':
        color_image = cv2.imread(path)
        depth_image = None

    elif encoding == 'depth':
        color_image = None
        depth_image = cv2.imread(path)

    elif encoding == 'both':
        ## TODO - figure out what filename should be for other given current
        color_image = None
        depth_image = cv2.imread(path)

    if color_image is None and encoding in ['color', 'both']:
        raise ValueError(f"Failed to read {path}!")
    if depth_image is None and encoding in ['depth', 'both']:
        raise ValueError(f"Failed to read {path}!")

    return [color_image, depth_image]


def read_annotations(path):
    """
    Read annoatations.

    Parameters
    ----------
    path: str
        Folder where Annotations folder is.

    Returns
    -------
    {filename: annotation}
    """
    annotation_folder = os.path.join(path, 'Annotations')

    annotations = {}
    for filename in os.listdir(annotation_folder):
        annotation = lxml.etree.parse(os.path.join(annotation_folder, filename)).getroot()

        annotations.update({filename.split('.')[0]: annotation})

    return annotations


def blank_dimensions(dimensions=None, generator=np.zeros, dtype='uint8'):
    """
    Generate series of blank images with set dimensions.

    Parameters
    ----------
    dimensions: Dict[name: (width, height)]
        Set of named image dimensions to generate.
    generator: func[height, width], default=np.zeros
        Function to generate images.
    dtype: np.dtype, default='uint8'
        Data type of image.

    Returns
    -------
    {str: (ndarray[3 channel], ndarray[1 channel])}
    """
    if dimensions is None:
        dimensions = {
            '480p blank': (640, 480),
            '720p blank': (1280, 720),
            '1080p blank': (1920, 1080),
            '4k blank': (4096, 2160),
        }

    if isinstance(dimensions, tuple):
        width, height = dimensions

        color_image = generator((height, width, 3), dtype=dtype)
        depth_image = generator((height, width), dtype=dtype)

        return color_image, depth_image

    output = {}
    for title, (width, height) in dimensions.items():
        color_image = generator((height, width, 3), dtype=dtype)
        depth_image = generator((height, width), dtype=dtype)

        output.update({title: (color_image, depth_image)})

    return output


def noise(amounts=None, dimensions=(1280, 720), generator=np.random.poisson, dtype='uint8'):
    """
    Generate series of images w/ varying amounts of noise.

    Parameters
    ----------
    amounts: Dict[name: amount]
        Set of named noise amounts to generate from.
    dimensions: (width, height)]
        Dimensions of images.
    generator: func[amount, height, width], default=np.random.poisson
        Function to generate images - note amounts in [0, 50 safe].
    dtype: np.dtype, default='uint8'
        Data type of image.

    Returns
    -------
    {str: (ndarray[3 channel], ndarray[1 channel])}
    """
    width, height = dimensions

    if amounts is None:
        amounts = {
            'sd=0': 0,
            'sd=1': 1,
            'sd=3': 8,
            'sd=6': 40,
            'sd=10': 100,
            'sd=14': 200,
        }

    if isinstance(amounts, (int, float)):
        color_image = generator(amounts, (height, width, 3)).astype(dtype)
        depth_image = generator(amounts, (height, width)).astype(dtype)

        return color_image, depth_image

    output = {}
    for title, amount in amounts.items():
        color_image = generator(amount, (height, width, 3)).astype(dtype)
        depth_image = generator(amount, (height, width)).astype(dtype)

        output.update({title: (color_image, depth_image)})

    return output
