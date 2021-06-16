import random
import sys
import os
import argparse
import logging
import time
from shutil import copyfile
from multiprocessing import Pool, Value, Lock

sys.path.append(r"C:\Users\thomas\Documents\GitHub\NCRF\venv\Lib\site-packages\openslide-win64-20171122\bin")
os.add_dll_directory(r"C:\Users\thomas\Documents\GitHub\NCRF\venv\Lib\site-packages\openslide-win64-20171122\bin")

import openslide

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

parser = argparse.ArgumentParser(description='Generate patches from a given '
                                 'list of coordinates')
parser.add_argument('wsi_path', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the input directory of WSI files')
parser.add_argument('coords_path', default=None, metavar='COORDS_PATH',
                    type=str, help='Path to the input list of coordinates')
parser.add_argument('patch_path', default=None, metavar='PATCH_PATH', type=str,
                    help='Path to the output directory of patch images')
parser.add_argument('patch_stage', default=None, metavar='PATCH_STAGE', type=str,
                    help='Patch Stage')
parser.add_argument('--patch_size', default=768, type=int, help='patch size, '
                    'default 768')
parser.add_argument('--level', default=0, type=int, help='level for WSI, to '
                    'generate patches, default 0')
parser.add_argument('--num_process', default=5, type=int,
                    help='number of mutli-process, default 5')
parser.add_argument('--num_samples', default=20000, type=int,
                    help='number of samples, default 20000')

count = Value('i', 0)
lock = Lock()


def process(opts):
    i, pid, x_center, y_center, args = opts
    if pid.split('_')[0] == 'Tumor':
        if 1<=int(pid.split('_')[-1].split('.')[0])<=70 or int(pid.split('_')[-1].split('.')[0]) == 111:
            center = 'Raboud'
        else:
            center = 'Utrecht'
    elif pid.split('_')[0] == 'Normal':
        if 1<=int(pid.split('_')[-1].split('.')[0])<=100:
            center = 'Raboud'
        else:
            center = 'Utrecht'

    x = int(int(x_center) - args.patch_size / 2)
    y = int(int(y_center) - args.patch_size / 2)

    if pid.split('_')[0] == 'Tumor':
        wsi_path = os.path.join(args.wsi_path, 'tumor', 'tumor' + '_' + pid.split('_')[1] + '.tif')
    if pid.split('_')[0] == 'Normal':
        wsi_path = os.path.join(args.wsi_path, 'normal', 'normal' + '_' + pid.split('_')[1] + '.tif')

    slide = openslide.OpenSlide(wsi_path)
    # print('level is ',args.level)
    img = slide.read_region(
        (x, y), args.level,
        (args.patch_size, args.patch_size)).convert('RGB')

    img.save(os.path.join(args.patch_path, center, args.patch_stage + '_' + str(i) + '.jpg'))
    img.save(os.path.join(args.patch_path, args.patch_stage, str(i) + '.jpg'))

    global lock
    global count

    with lock:
        count.value += 1
        if (count.value) % 100 == 0:
            logging.info('{}, {} patches generated...'
                         .format(time.strftime("%Y-%m-%d %H:%M:%S"),
                                 count.value))

def run(args):
    logging.basicConfig(level=logging.INFO)

    if not os.path.exists(args.patch_path):
        os.mkdir(args.patch_path)

    copyfile(args.coords_path, os.path.join(args.patch_path, 'list.txt'))

    opts_list = []
    infile = open(args.coords_path)

    # sample N lines
    lines = infile.readlines()
    selected_lines = random.choices(lines, k=args.num_samples)

    for i, line in enumerate(selected_lines):
        pid, x_center, y_center = line.strip('\n').split(',')
        opts_list.append((i, pid, x_center, y_center, args))
    infile.close()

    pool = Pool(processes=args.num_process)
    pool.map(process, opts_list)


def main():
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
