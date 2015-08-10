import csv
import numpy
import argparse

from itertools import product

def coords(x_size, y_size, x_min, y_min, x_step, y_step):
    cartesian_iterator = product(numpy.arange(x_size), numpy.arange(y_size))
    for x, y in cartesian_iterator:
        yield x, y, x_min + (x * x_step), y_min + (y * y_step)

def geotiff_to_csv(x, y, x_min, y_min, x_step, y_step, output):
    with open(output, 'w') as of:
        writer = csv.writer(of)
        for coord in coords(x, y, x_min, y_min, x_step, y_step):
            writer.writerow(coord + (0,))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=int)
    parser.add_argument('y', type=int)
    parser.add_argument('x_min', type=float)
    parser.add_argument('y_min', type=float)
    parser.add_argument('x_step', type=float)
    parser.add_argument('y_step', type=float)
    parser.add_argument('output_file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    geotiff_to_csv(args.x, args.y, args.x_min, args.y_min, args.x_step, args.y_step, args.output_file)




