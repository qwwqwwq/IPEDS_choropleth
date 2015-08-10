package com.pairwise;

import com.google.common.base.Joiner;
import com.google.common.base.Splitter;

import java.io.Serializable;
import java.util.Iterator;

public class RasterPoint implements Serializable {
    private double value;
    private final double x;
    private final double y;
    private final long xIndex;
    private final long yIndex;

    public RasterPoint(String record) {
        Iterable<String> split = Splitter.on(",").split(record);
        Iterator<String> iterator = split.iterator();
        this.xIndex = Long.parseLong(iterator.next());
        this.yIndex = Long.parseLong(iterator.next());
        this.x = Double.parseDouble(iterator.next());
        this.y = Double.parseDouble(iterator.next());
        this.value = Double.parseDouble(iterator.next());
    }

    public void setValue(double value) {
        this.value = value;
    }

    public double getValue() {
        return value;
    }

    public String toCsvString() {
        return Joiner.on(",").join(new Object[] {xIndex, yIndex, x, y, value});
    }

    public Coordinate getCoordinate() {
        return new Coordinate(x, y);
    }
}
