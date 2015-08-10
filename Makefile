all: gis/lower_48_contour.topojson

gis/cb_2014_us_state_20m.zip:
	wget -O gis/cb_2014_us_state_20m.zip "http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_state_20m.zip"

gis/gebco_08_rev_elev_A1_grey_geo.tif:
	wget -O gis/gebco_08_rev_elev_A1_grey_geo.tif "http://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73934/gebco_08_rev_elev_A1_grey_geo.tif"

gis/gebco_08_rev_elev_B1_grey_geo.tif:
	wget -O gis/gebco_08_rev_elev_B1_grey_geo.tif "http://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73934/gebco_08_rev_elev_B1_grey_geo.tif"

ipeds_data/hd2013.csv:
	wget -O ipeds_data/HD2013.zip "http://nces.ed.gov/ipeds/datacenter/data/HD2013.zip"
	cd ipeds_data && unzip HD2013.zip
	touch ipeds_data/hd2013.csv

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
	PYTHONPATH=py python py/gen_map_dataset.py ipeds_data/institution_coordinates_data.csv

gis/gebco_08_rev_elev_AB_grey_geo.tif: gis/gebco_08_rev_elev_B1_grey_geo.tif gis/gebco_08_rev_elev_A1_grey_geo.tif
	gdalwarp gis/gebco_08_rev_elev_B1_grey_geo.tif gis/gebco_08_rev_elev_A1_grey_geo.tif gis/gebco_08_rev_elev_AB_grey_geo.tif

gis/gebco_08_rev_elev_AB_grey_geo_resample.tif: gis/gebco_08_rev_elev_AB_grey_geo.tif
	gdalwarp -tr 0.05 -0.05 -r average gis/gebco_08_rev_elev_AB_grey_geo.tif gis/gebco_08_rev_elev_AB_grey_geo_resample.tif

gis/lower_48_dem.tif: gis/us_lower_48_states.shp gis/gebco_08_rev_elev_AB_grey_geo_resample.tif
	gdalwarp -overwrite -of GTiff -cutline gis/us_lower_48_states.shp \
		-crop_to_cutline gis/gebco_08_rev_elev_AB_grey_geo_resample.tif \
		gis/lower_48_dem.tif

gis/raster_coordinates_data.csv: gis/lower_48_dem.tif
	python py/geotiff_to_csv.py gis/lower_48_dem.tif gis/raster_coordinates_data.csv

gis/raster_coordinates_reclassed.csv: gis/raster_coordinates_data.csv ipeds_data/institution_coordinates_data.csv java/target/pairwise-1.0-SNAPSHOT.jar
	PYTHONPATH=py python py/distributed_pairwise_distance.py \
	    --raster_csv gis/raster_coordinates_data.csv \
	    --institution_csv ipeds_data/institution_coordinates_data.csv \
	    --jar java/target/pairwise-1.0-SNAPSHOT.jar \
	    --output_s3_bucket jq-emr-bucket \
	    --output_s3_prefix ipeds_pairwise`date +"%m%d%Y-%H-%M-%S"` \
	    --output_file gis/raster_coordinates_reclassed.csv

gis/lower_48_dem_reclassed.tif: gis/raster_coordinates_reclassed.csv gis/lower_48_dem.tif
	PYHTONPATH=py python py/reclass_raster.py gis/lower_48_dem.tif gis/raster_coordinates_reclassed.csv gis/lower_48_dem_reclassed_s.tif
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
