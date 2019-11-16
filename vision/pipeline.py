import os
import json
from vision.realsense.read_bag import ReadBag
from vision.blob.blobfind import import_params, BlobFinder
from vision.util.blob_plotter import plot_blobs

prefix = 'vision' if os.path.isdir("vision") else ''
config_filename = os.path.join(prefix, 'blob', 'config.json')

with open(config_filename, 'r') as config_file:
    config = json.load(config_file)

video_file_name = os.path.join('vision_videos', 'module', 'sampleFrames.bag')
for i, (depth_image, color_image) in enumerate(ReadBag(video_file_name)):
    if i == 98:
        break
    blob_finder = BlobFinder(color_image, params=import_params(config))
    bboxes = blob_finder.find()

    plot_blobs(blob_finder.keypoints, color_image)
