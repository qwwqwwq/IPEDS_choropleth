# IPEDS Choropleth

Choropleth map of college density in the U.S.

## Datasets

- 2014 TIGER/Line Shapefiles (machinereadable data files) / prepared by the U.S. Census Bureau, 2014 (https://www.census.gov/geo/maps-data/data/tiger.html)
- Integrated Postsecondary Education Data System (IPEDS), 2013 survey data (http://nces.ed.gov/ipeds/)


## Dependencies

- gdal (and python bindings)
- maven
- spark
- numpy / pandas

## Build

To build the topojson using local calculation of the density metrics, run:

`make all`

The density metric calculation takes a little while (about 10 mins), and if we ever want to do a higher resolution map,
it will be too much for one machine. So for this Makefile there is an option to run the density metric calculations on
 a remote Spark cluster hosted by Amazon Web Services.

To choose this option run:

`make s3_bucket=<s3 bucket> all`

The step in the Makefile that calculates the density metric will attempt to run a Spark job via the
Amazon Elastic Mapreduce service and store temporary results in `s3_bucket`. Running this assumes that you
have a valid `~/.aws/credentials` file installed. The cost of this job should be ~$3.00.

## Methods
The basic method for creating this visualization is:

- Generate a list of raster coordinates for spanning the continental united states
- For each coordinate, calculate a metric based on the pairwise distance to every institution listed in the IPEDs data set
(see formula and inclusion criteria for institutions below)
- Reconstruct the CSV of metric values at each raster coordinate into a GeoTIFF file
- Zero out all pixels that fall outside the boundaries of the continental US
- Create polygons for all pixels above a certain metric cutoff, and combine into a topojson file with state boundaries.

### Inclusion Criteria

We include all IPEDs institutions where the highest level of offering is at least a Bachelor's degree
(HLOFFER >= 5 and UGOFFER == 1) and where the size of the institution is reported (INSTSIZE != null).
This filters out 2860/7764 of the IPEDS institutions.

### College Density Metric

The formula for the college density is the sum of the inverse distance from that point to each institution, multiplied
nu the INSTSIZE of that institution, which is a number between 1 and 5. This is not an idea variable for size, but
the completeness of the other institutional size variables in the IPEDS dataset is surprisingly low,
and seeing as this is just for visualization, it accomplishes the goal of weeding out false density from the super tiny schools.
