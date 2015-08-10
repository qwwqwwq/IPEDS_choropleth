package com.pairwise;

import java.io.Serializable;

public class Coordinate implements Serializable {
    private final Double longitude;
    private final Double latitude;

    public Coordinate(Double longitude, Double latitude) {
        this.longitude = longitude;
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }


    public Double getLatitude() {
        return latitude;
    }
}
