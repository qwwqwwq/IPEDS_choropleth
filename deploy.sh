aws s3 cp index.html s3://ipeds-visualization
aws s3 cp --recursive static s3://ipeds-visualization/static
aws s3 cp gis/lower_48_contour.topojson s3://ipeds-visualization/gis/lower_48_contour.topojson
