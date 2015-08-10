package com.pairwise;

import junit.framework.TestCase;

public class RasterPointTest extends TestCase {

    public void testRasterPoint() throws Exception {
        RasterPoint rasterPoint = new RasterPoint("1,2,10.0,20.0,0");
        rasterPoint.setValue(1.0);
        assertEquals(rasterPoint.toCsvString(), "1,2,10.0,20.0,1.0");
        assertEquals(rasterPoint.getCoordinate().getLongitude(), 10.0);
        assertEquals(rasterPoint.getCoordinate().getLatitude(), 20.0);
    }
}