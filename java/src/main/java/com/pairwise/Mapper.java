package com.pairwise;

import org.apache.commons.csv.CSVFormat;
import org.apache.spark.api.java.function.Function;
import org.apache.spark.broadcast.Broadcast;

import java.util.List;

public class Mapper implements Function<String, String> {

    private final Broadcast<List<InstitutionPoint>> broadcast;

    public Mapper(Broadcast<List<InstitutionPoint>> broadcast) {
        this.broadcast = broadcast;
    }

    @Override
    public String call(String s) throws Exception {
        RasterPoint rasterPoint = new RasterPoint(s);
        Double metric = 0.0;

        for (InstitutionPoint institutionPoint : broadcast.getValue()) {
            metric += institutionPoint.getSizeFactor() /
                    Haversine.dist(institutionPoint.getCoordinate(), rasterPoint.getCoordinate());

        }
        rasterPoint.setValue(metric);
        return rasterPoint.toCsvString();
    }
}
