package com.pairwise;

import com.google.common.base.Splitter;
import com.google.common.collect.Lists;
import junit.framework.TestCase;
import org.apache.spark.broadcast.Broadcast;

import java.util.List;

import static org.mockito.Mockito.*;

public class MapperTest extends TestCase {

    private static final String EXAMPLE = "1,2,10.0,20.0,0";

    @SuppressWarnings("unchecked")
    public void testCall() throws Exception {
        Broadcast<List<InstitutionPoint>> mockBroadcast = (Broadcast<List<InstitutionPoint>>) mock(Broadcast.class);
        when(mockBroadcast.getValue())
                .thenReturn(Lists.newArrayList(
                        new InstitutionPoint(new Coordinate(10.0, 10.0), 1.0),
                        new InstitutionPoint(new Coordinate(20.0, 20.0), 2.0)
                ));

        Mapper mapper = new Mapper(mockBroadcast);

        String mappedValue = mapper.call(EXAMPLE);
        assertTrue(mappedValue.startsWith("1,2,10.0,20.0,"));
        String value = Splitter.on(",").splitToList(mappedValue).get(4);
        assertTrue(Double.parseDouble(value) > 0.0);
    }
}