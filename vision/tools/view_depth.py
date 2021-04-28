"""
Visualize all depth images in given directory.

In windows, as is this will display all images in console directory.
In linux, as is this will display all images in tools/.
"""
import os

import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    FOLDER = "."

    for filename in os.listdir(FOLDER):
        if ".npy" not in filename:
            continue

        with open(os.path.join(FOLDER, filename), "rb") as file:
            nd = np.load(file)

        plt.imshow(nd)
        plt.show()
