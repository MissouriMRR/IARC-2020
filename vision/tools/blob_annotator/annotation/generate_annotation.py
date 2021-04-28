"""
Utility functions for creating Pascal VOC style annotations

Multi-Rotor Robot Design Team
Missouri University of Science and Technology
Fall 2017
Christopher O'Toole
"""
import os
import cv2
import numpy as np
from lxml import etree


ROOT_NAME = "annotation"
OBJECT_ELEMENT_NAME = "object"
ANNOTATION_DEFAULT_DIR = "Annotations"


def _generate_xml_element_with_text(name, text):
    """generate a xml element with a text value"""
    element = etree.Element(name)
    element.text = str(text)
    return element


def _generate_object_annotation(obj_name, bbox, width, height):
    """generate an object annotation Pascal VOC style"""
    xmin, ymin, xmax, ymax = bbox

    obj = etree.Element(OBJECT_ELEMENT_NAME)
    obj.append(_generate_xml_element_with_text("name", obj_name))
    obj.append(_generate_xml_element_with_text("truncated", 0))
    obj.append(_generate_xml_element_with_text("difficult", 0))

    bndbox = etree.Element("bndbox")
    bndbox.append(_generate_xml_element_with_text("xmin", min(max(0, xmin), width)))
    bndbox.append(_generate_xml_element_with_text("ymin", min(max(0, ymin), height)))
    bndbox.append(_generate_xml_element_with_text("xmax", min(max(0, xmax), width)))
    bndbox.append(_generate_xml_element_with_text("ymax", min(max(0, ymax), height)))
    obj.append(bndbox)

    return obj


def generate_pascalvoc_annotation_from_image(
    img, obj_names, bboxes, file_path, img_path, overwrite=False
):
    """
    Generates a Pascal VOC annotation file for `img` with the specified parameters

    Parameters
    ----------
    img: numpy.ndarray
        Image to annotate
    obj_names: collection of str
        Human-readable label for each object present in the image
    bboxes: collection of sequences of form (xmin, ymin, xmax, ymax)
        Bounding boxes for each object present in the image
    file_path: str
        Path which the annotation file will be written to
    overwrite: bool, optional
        Optional parameter specifying if an existing annotations
        should be overwritten, defaults to False
    """
    height, width, depth = img.shape

    root = etree.Element(ROOT_NAME)

    size = etree.Element("size")
    size.append(_generate_xml_element_with_text("width", width))
    size.append(_generate_xml_element_with_text("height", height))
    size.append(_generate_xml_element_with_text("depth", depth))
    root.append(size)

    path = etree.Element("path")
    path.append(_generate_xml_element_with_text("value", os.path.basename(img_path)))
    root.append(path)

    for obj_name, bbox in zip(obj_names, bboxes):
        box = bbox.box
        compat_bbox = (box.x, box.y, box.x1, box.y1)
        root.append(_generate_object_annotation(obj_name, compat_bbox, width, height))

    if not overwrite:
        assert not os.path.exists(
            file_path
        ), "generate_pascalvoc_annotation_from_image(): %s already exists!" % (
            file_path,
        )

    with open(file_path, "wb") as out_file:
        out_file.write(etree.tostring(root, pretty_print=True))


def generate_pascvalvoc_annotation_from_image_file(
    img_path, obj_names, bboxes, annotation_dir=None, overwrite=False
):
    """
    Generates a Pascal VOC annotation file for `img_path` with the specified parameters
    Parameters
    ----------
    img_path: str
        Path to image to annotate
    obj_names: collection of str
        Human-readable label for each object present in the image
    bboxes: collection of sequences of form (xmin, ymin, xmax, ymax)
        Bounding boxes for each object present in the image
    annotation_dir: str, optional
        Optional parameter specifying a folder to store the annotation file in
    overwrite: bool, optional
        Optional parameter specifying if an existing annotations should be overwritten, defaults to False
    """

    img_file_name, _ = os.path.splitext(img_path)
    img = cv2.imread(img_path)
    assert img is not None, (
        "generate_pascvalvoc_annotation_from_image_file(): could not read image at %s"
        % (img_path,)
    )

    if annotation_dir is None:
        generate_pascalvoc_annotation_from_image(
            img,
            obj_names,
            bboxes,
            img_file_name + ".xml",
            img_path="",
            overwrite=overwrite,
        )
    else:
        img_folder = os.path.dirname(img_file_name)
        img_name = os.path.basename(img_file_name)
        annotation_folder = os.path.join(img_folder, annotation_dir)

        if not os.path.exists(annotation_folder):
            os.mkdir(annotation_folder)

        generate_pascalvoc_annotation_from_image(
            img,
            obj_names,
            bboxes,
            os.path.join(annotation_folder, img_name) + ".xml",
            img_path,
            overwrite=overwrite,
        )


if __name__ == "__main__":
    # unit test
    TEST_IMG_NAME = ""
    obj_names = ["red roomba", "green roomba"]
    bboxes = np.array([[548, 472, 878, 753], [697, 293, 982, 531]])
    generate_pascvalvoc_annotation_from_image_file(
        TEST_IMG_NAME, obj_names, bboxes, annotation_dir=ANNOTATION_DEFAULT_DIR
    )
