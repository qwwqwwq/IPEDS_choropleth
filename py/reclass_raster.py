import numpy
import sys
import argparse
import pandas
from osgeo import gdal
from osgeo.gdalconst import *

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=int)
    parser.add_argument('y', type=int)
    parser.add_argument('x_min', type=float)
    parser.add_argument('y_min', type=float)
    parser.add_argument('x_step', type=float)
    parser.add_argument('y_step', type=float)
    parser.add_argument('incsv')
    parser.add_argument('outfile')
    return parser.parse_args()

def get_new_arr(fn, x, y):
    df = pandas.read_csv(fn, names=['x', 'y', 'lon', 'lat', 'value'])
    return numpy.uint16(numpy.reshape((df.sort(['x', 'y']).value).round(), (y, x)).T)

def reclass(csv_fn, rows, cols, x_min, y_min, x_step, y_step, ofn):
    # register all of the GDAL drivers
    gdal.AllRegister()

    new_arr = get_new_arr(csv_fn, cols, rows)

    # create the output image
    driver = gdal.GetDriverByName("GTiff")
    #print driver
    outDs = driver.Create(ofn, rows, cols, 1, GDT_UInt16)
    if outDs is None:
        print ofn
        sys.exit(1)

    outBand = outDs.GetRasterBand(1)
    # write the data
    outBand.WriteArray(new_arr, 0, 0)

    # flush data to disk, set the NoData value and calculate stats
    outBand.FlushCache()
    outBand.SetNoDataValue(0)

    # georeference the image and set the projection
    outDs.SetGeoTransform((x_min,
                           x_step,
                           0.0,
                           y_min,
                           0.0,
                           y_step))
    outDs.SetProjection('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')

def main():
    args = get_args()
    reclass(args.incsv, args.x, args.y, args.x_min, args.y_min, args.x_step, args.y_step, args.outfile)

if __name__ == '__main__':
    main()
