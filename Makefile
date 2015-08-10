all: gis/lower_48_contour.topojson

gis/cb_2014_us_state_20m.zip:
	wget -O gis/cb_2014_us_state_20m.zip "http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_state_20m.zip"

ipeds_data/hd2013.csv:
	wget -O ipeds_data/HD2013.zip "http://nces.ed.gov/ipeds/datacenter/data/HD2013.zip"
	wget -O ipeds_data/HD2013_Dict.zip "http://nces.ed.gov/ipeds/datacenter/data/HD2013_Dict.zip"
	cd ipeds_data && unzip HD2013.zip && unzip HD2013_Dict.zip
	touch ipeds_data/hd2013.csv
	touch ipeds_data/hd2013.xlsx

java/target/pairwise-1.0-SNAPSHOT.jar:
	cd java && mvn clean package

gis/cb_2014_us_state_20m.shp: gis/cb_2014_us_state_20m.zip
	cd gis && unzip cb_2014_us_state_20m.zip
	touch gis/cb_2014_us_state_20m.shp

gis/cb_2014_us_state_20m_reproj.shp: gis/cb_2014_us_state_20m.shp
	ogr2ogr -t_srs EPSG:5070 gis/cb_2014_us_state_20m_reproj.shp gis/cb_2014_us_state_20m.shp

gis/us_lower_48_states_individual.shp: gis/cb_2014_us_state_20m_reproj.shp
	ogr2ogr -where "STUSPS != 'AK' AND STUSPS != 'HI' AND STUSPS != 'PR'" gis/us_lower_48_states_individual.shp gis/cb_2014_us_state_20m_reproj.shp

gis/us_lower_48_states.shp: gis/us_lower_48_states_individual.shp
	ogr2ogr gis/us_lower_48_states.shp gis/us_lower_48_states_individual.shp  -dialect sqlite -sql "SELECT ST_Union(geometry) FROM us_lower_48_states_individual"

ipeds_data/institution_coordinates_data.csv: ipeds_data/hd2013.csv
	PYTHONPATH=py python py/generate_institution_coords_csv.py ipeds_data/institution_coordinates_data.csv

gis/raster_coordinates_data.csv:
	python py/generate_raster_csv.py 1156 498 -124.7258390 49.3843580 0.05 -0.05 gis/raster_coordinates_data.csv

gis/raster_coordinates_reclassed.csv: gis/raster_coordinates_data.csv ipeds_data/institution_coordinates_data.csv java/target/pairwise-1.0-SNAPSHOT.jar
ifndef $(s3_bucket)
	spark-submit --master local[2] --class com.pairwise.PairwiseDistanceLocal java/target/pairwise-1.0-SNAPSHOT.jar ipeds_data/institution_coordinates_data.csv gis/raster_coordinates_data.csv tmp/ 2
	cat tmp/* > gis/raster_coordinates_reclassed.csv
	rm -rf tmp/
else
	PYTHONPATH=py python py/distributed_pairwise_distance.py \
	    --raster_csv gis/raster_coordinates_data.csv \
	    --institution_csv ipeds_data/institution_coordinates_data.csv \
	    --jar java/target/pairwise-1.0-SNAPSHOT.jar \
	    --output_s3_bucket $(s3_bucket) \
	    --output_s3_prefix ipeds_pairwise`date +"%m%d%Y-%H-%M-%S"` \
	    --output_file gis/raster_coordinates_reclassed.csv
endif

gis/lower_48_dem_reclassed.tif: gis/raster_coordinates_reclassed.csv
	PYHTONPATH=py python py/reclass_raster.py 1156 498 -124.7258390 49.3843580 0.05 -0.05 gis/raster_coordinates_reclassed.csv gis/lower_48_dem_reclassed_s.tif
	gdalwarp -t_srs EPSG:5070 -of GTiff -cutline gis/us_lower_48_states.shp \
		-crop_to_cutline gis/lower_48_dem_reclassed_s.tif gis/lower_48_dem_reclassed.tif

gis/levels.shp: gis/lower_48_dem_reclassed.tif
	for level in 1 2 3 4 5 7 9 10 12 15 20 25 30 35 40 50 ; do \
        gdal_calc.py -A gis/lower_48_dem_reclassed.tif --outfile=gis/level$$level.tif --calc="$$level*(A>$$level)" --NoDataValue=0 && \
        gdal_polygonize.py gis/level$$level.tif -f "ESRI Shapefile" gis/level$$level.shp contour elevation && \
        ogr2ogr -update -append gis/levels.shp gis/level$$level.shp ; \
	done

gis/lower_48_contour.topojson: gis/levels.shp
	topojson -p -o gis/lower_48_contour.topojson --width 900 gis/levels.shp gis/us_lower_48_states_individual.shp
