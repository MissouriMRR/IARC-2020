"""
Display BoundingBoxes on image.
"""
import cv2
import numpy as np


BBOX_COLOR = (0, 255, 0)
BBOX_THICKNESS = 2


def plot_box(
    boxes: list,
    image: np.ndarray,
    waittime: int = 0,
    save_img: bool = False,
    path: str = "plot_imgs",
    quiet_output: bool = False
) -> None:
    """
    Display BoundingBoxes on image.

    Parameters
    ----------
    boxes: list[BoundingBox]
        List of bounding boxes to plot on image.
    image: np.ndarray
        image to detect obstacles in
    waittime: int, default=0
        cv2.waitKey parameter, number of seconds to show window 0=inf.
    save_img: bool
        Whether to save the image with the boxes plotted.
    path: str
        Where to save image to if save_img is True. Should include filename and extension.
    """
    if not isinstance(boxes, list):
        raise ValueError(f"Expected list of BoundingBox, got {type(boxes)} instead")
    if not isinstance(image, np.ndarray):
        raise ValueError(
            f"Expected argument of type ObstacleFinder, got {type(image)} instead"
        )

    output = np.copy(image)  # Important so dont have to copy before passing here
    for bbox in boxes:
        if not bbox.vertices:
            continue
        # print(bbox.vertices)
        X, Y = [], []
        for pair in bbox.vertices:
            x, y = pair[0], pair[1]

            x, y = int(x), int(y)

            X.append(x)
            Y.append(y)

        cv2.rectangle(
            output, (min(X), min(Y)), (max(X), max(Y)), BBOX_COLOR, BBOX_THICKNESS
        )

        if not quiet_output:
            print('\tKeypoint:', bbox.pt[0], bbox.pt[1])

        # visualize keypoints
        # output = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(255, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    if not save_img:
        cv2.imshow("Obstacles", output)
        cv2.waitKey(waittime)
    else:
        cv2.imwrite(filename=path, img=output)
