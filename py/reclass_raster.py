import numpy
import sys
import argparse
import pandas
from osgeo import gdal
from osgeo.gdalconst import *

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('incsv')
    parser.add_argument('outfile')
    return parser.parse_args()

def get_new_arr(fn, x, y):
    df = pandas.read_csv(fn, names=['x', 'y', 'lon', 'lat', 'value'])
    return numpy.uint16(numpy.reshape((df.sort(['x', 'y']).value).round(), (y, x)).T)

def reclass(geotiff_fn, csv_fn, ofn):
    # register all of the GDAL drivers
    gdal.AllRegister()

    # open the image
    inDs = gdal.Open(geotiff_fn)
    if inDs is None:
        print 'Could not open image file'
        sys.exit(1)

    # read in the crop data and get info about it
    band1 = inDs.GetRasterBand(1)
    rows = inDs.RasterYSize
    cols = inDs.RasterXSize

    new_arr = get_new_arr(csv_fn, rows, cols)

    # create the output image
    driver = inDs.GetDriver()
    #print driver
    outDs = driver.Create(ofn, cols, rows, 1, GDT_UInt16)
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
    outDs.SetGeoTransform(inDs.GetGeoTransform())
    outDs.SetProjection(inDs.GetProjection())

def main():
    args = get_args()
    reclass(args.infile, args.incsv, args.outfile)

if __name__ == '__main__':
    main()
