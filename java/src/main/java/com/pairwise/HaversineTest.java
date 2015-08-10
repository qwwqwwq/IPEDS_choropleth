package com.pairwise;

import junit.framework.TestCase;

public class HaversineTest extends TestCase {

    public void testDist() throws Exception {
        assertEquals(Haversine.dist(
                new Coordinate(50.0359, -5.4243),
                new Coordinate(58.3838, -3.0412)
        ), 962823.1, 1.0);

    }
}