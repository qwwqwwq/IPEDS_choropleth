# Version of the pariwise distance calculation that runs locally
# Would probably take a long time to finish.. Maybe > 1hr
import argparse
import csv

from math import radians, cos, sin, asin, sqrt, pow


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    lon1, lat1 = point1
    lon2, lat2 = point2
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def csv_points(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            yield (float(row[0]), float(row[1]))


def instituion_points(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield ((float(row['LONG']), float(row['LAT'])), float(row['SIZECAT']))


def get_distances(area_file, points_of_interest_file, output_file):
    with open(output_file, "w") as of:
        writer = csv.writer(of)
        for area_point in csv_points(area_file):
            distance = 0
            for poi_point, size_category in instituion_points(points_of_interest_file):
                distance += size_category / pow(haversine(area_point, poi_point[:2]), 2)
            writer.writerow([area_point[0], area_point[1], distance])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('area_file')
    parser.add_argument('poi_file')
    parser.add_argument('output_file')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    get_distances(args.area_file, args.poi_file, args.output_file)
