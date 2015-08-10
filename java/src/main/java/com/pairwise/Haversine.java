package com.pairwise;

/**
 * Calculate great circle distance between two lat/long coordinates in kilometers
 */
public class Haversine {

    private static final Double EARTH_RADIUS = 6371.0;

    public static double dist(Coordinate a, Coordinate b) {
        double dLat  = Math.toRadians((b.getLatitude() - a.getLatitude()));
        double dLong = Math.toRadians((b.getLongitude() - a.getLongitude()));

        double startLat = Math.toRadians(a.getLatitude());
        double endLat = Math.toRadians(b.getLatitude());

        double arc = haversin(dLat) + Math.cos(startLat) * Math.cos(endLat) * haversin(dLong);
        double c = 2 * Math.atan2(Math.sqrt(arc), Math.sqrt(1 - arc));

        return EARTH_RADIUS * c;
    }

    private static double haversin(double val) {
        return Math.pow(Math.sin(val / 2), 2);
    }
}
