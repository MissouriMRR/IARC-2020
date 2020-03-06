"""
Record a realsense video.
"""
import os
import pyrealsense2 as rs


if __name__ == '__main__':
    FILENAME = 'realsense_video'

    number = -1

    for filename in os.listdir('.'):
        if FILENAME in filename:
            file_number = int(filename.replace(FILENAME, '').replace('.bag', ''))

            number = max(number, file_number)

    FILENAME += f'{number + 1}.bag'

    ##
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, 1080, 720, 30)
    config.enable_stream(rs.stream.color, 1080, 720, 30)

    config.enable_record_to_file(FILENAME)

    ##
    pipeline.start(config)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

    finally:
        pipeline.stop()
