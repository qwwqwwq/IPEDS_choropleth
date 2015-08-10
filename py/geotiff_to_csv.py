import csv
import gdal
import numpy
import argparse
from PIL import Image

from itertools import product

def coords(x_size, y_size, x_min, y_min, x_step, y_step):
    cartesian_iterator = product(numpy.arange(x_size), numpy.arange(y_size))
    for x, y in cartesian_iterator:
        yield x, y, x_min + (x * x_step), y_min + (y * y_step)

def geotiff_to_csv(geotiff, output):
    i = gdal.Open(geotiff)
    data = numpy.array(Image.open(geotiff))
    x_size = i.RasterXSize
    y_size = i.RasterYSize
    x_min, x_step_x, x_step_y, y_min, y_step_x, y_step_y = i.GetGeoTransform()

    with open(output, 'w') as of:
        writer = csv.writer(of)
        for coord in coords(x_size, y_size, x_min, y_min, x_step_x, y_step_y):
            value = data[(coord[1], coord[0])]
            writer.writerow(coord + (value,))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('geotiff_file')
    parser.add_argument('output_file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    geotiff_to_csv(args.geotiff_file, args.output_file)




