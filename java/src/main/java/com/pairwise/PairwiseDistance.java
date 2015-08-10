package com.pairwise;

import com.google.common.collect.Lists;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.broadcast.Broadcast;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class PairwiseDistance {
    public static void main(String[] args) throws IOException {
        SparkConf conf = new SparkConf().setAppName("Pairwise distance");
        JavaSparkContext sc = new JavaSparkContext(conf);

        Broadcast<List<InstitutionPoint>> broadcast = sc.broadcast(read(Paths.get(args[0])));

        JavaRDD<String> rasterCoordinates = sc.textFile(args[1], Integer.parseInt(args[3]));
        JavaRDD<String> mapped = rasterCoordinates.map(new Mapper(broadcast));
        mapped.saveAsTextFile(args[2]);
    }


    public static List<InstitutionPoint> read(Path path) throws IOException {
        CSVParser csvParser = CSVParser.parse(path.toFile(), StandardCharsets.UTF_8,
                CSVFormat.RFC4180.withHeader("UNITID", "NAME", "SIZECAT", "LONG", "LAT"));
        List<InstitutionPoint> output = Lists.newArrayList();
        for (CSVRecord record : csvParser) {
            output.add(new InstitutionPoint(
                    new Coordinate(
                            Double.parseDouble(record.get("LONG")),
                            Double.parseDouble(record.get("LAT"))),
                    Double.parseDouble(record.get("SIZECAT"))));
        }
        return output;
    }
}
