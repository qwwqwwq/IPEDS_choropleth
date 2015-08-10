package com.pairwise;

import java.io.Serializable;

public class InstitutionPoint implements Serializable {
        private final Double sizeFactor;
        private final Coordinate coordinate;

        public Double getSizeFactor() {
            return sizeFactor;
        }

        public Coordinate getCoordinate() {
            return coordinate;
        }

        public InstitutionPoint(Coordinate coordinate, Double sizeFactor) {
            this.coordinate = coordinate;
            this.sizeFactor = sizeFactor;
        }
}
