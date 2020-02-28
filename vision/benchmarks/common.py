"""
Common functions for benchmarks to make use of.
"""
import numpy as np


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

    output = {}
    for title, (width, height) in dimensions.items():
        color_image = generator((height, width, 3), dtype=dtype)
        depth_image = generator((height, width), dtype=dtype)

        output.update({title: (color_image, depth_image)})

    return output


def noise(amounts=None, dimensions=(1280, 720), generator=np.random.poisson, scalar=2, dtype='uint8'):
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
    scalar: int or float, default=2
        Amount to scale generated values by.
    dtype: np.dtype, default='uint8'
        Data type of image.

    Returns
    -------
    {str: (ndarray[3 channel], ndarray[1 channel])}
    """
    if amounts is None:
        amounts = {
            'sd=0': 0,
            'sd=1': .25,
            'sd=3': 2,
            'sd=6': 10,
            'sd=10': 25,
            'sd=14': 50,
        }

    width, height = dimensions

    output = {}
    for title, amount in amounts.items():
        color_image = generator(amount, (height, width, 3)).astype(dtype)
        depth_image = generator(amount, (height, width)).astype(dtype)

        color_image, depth_image = map(lambda v: np.int_(v * scalar), [color_image, depth_image])

        output.update({title: (color_image, depth_image)})

    return output
