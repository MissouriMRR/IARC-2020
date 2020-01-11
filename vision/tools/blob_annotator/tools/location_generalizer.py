# Use pillow to create images and then place the given image on it at varying points

from os import listdir, remove
from PIL import Image


BG_W = 1920
BG_H = 1080

IMG_DIRECTORY = r"input/"

OUT_DIRECTORY = r"output/"

GRANULARITY = 4


def fresh_background():
    return Image.new('RGBA', (BG_W, BG_H), (255, 255, 255, 255))


def generate(img, out_dir):
    img_w, img_h = img.size
    half_w, half_h = int(img_w/2), int(img_h/2)

    for x in range(-half_w, BG_W - half_w, half_w * GRANULARITY):
        for y in range(-half_h, BG_H - half_h, half_h * GRANULARITY):
            background = fresh_background()

            offset = (x, y)

            background.paste(img, offset)

            background.save('{}{}-{}x{}.png'.format(out_dir, img.filename.split('/')[-1], x, y))


def generate_directory(directory, out_dir):
    for filename in listdir(directory):
        img = Image.open(directory + filename, 'r')

        generate(img, out_dir)


def clean_directory(directory):
    for filename in listdir(directory):
        remove(directory + filename)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument("-c", "--clean", dest="clean", action="store_true",\
                        help="Clean target directory before generating.")

    parser.add_argument("-d", "--disable-generator", dest="disable_generator", action="store_true",\
                        help="Disable generator and clean.")

    options = parser.parse_args()

    if options.clean or options.disable_generator:
        clean_directory(OUT_DIRECTORY)

    if not options.disable_generator:
        generate_directory(IMG_DIRECTORY, OUT_DIRECTORY)
