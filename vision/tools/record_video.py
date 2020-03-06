"""
Record a realsense video.

When done, press ctrl-c once and give it a second to close up.
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

    config.enable_stream(rs.stream.depth, 0, 0, rs.format.z16, 0)
    config.enable_stream(rs.stream.color, 0, 0, rs.format.bgr8, 0)

    config.enable_record_to_file(FILENAME)

    ##
    pipeline.start(config)

    try:
        i = 0
        while True:
            i += 1
            frames = pipeline.wait_for_frames()

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                print("Failed to capture image.")
                continue

    except Exception as e:
        print(e)

    pipeline.stop()
