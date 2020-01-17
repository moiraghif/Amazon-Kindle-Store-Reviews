package main;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.types._;
import org.apache.spark.sql.functions._;

import statistics.functions._;


object TextMining {

  def main(args: Array[String]) {

    // initialize Spark
    val spark: SparkSession = SparkSession.builder()
      .appName("TextMining with Spark & Scala")
      .getOrCreate();
    spark.sparkContext.setLogLevel("ERROR");  // just to have a less verbose output


    // get input data and split text into tokens
    val path: String = "hdfs://localhost:9000/TextMining/tokens/";

    // "rate" must be Double because it can be easily binarized by Spark
    val original_schema = new StructType(Array(
      StructField("product", StringType,  true),
      StructField("votes",   IntegerType, true),
      StructField("rate",    DoubleType,  true),
      StructField("text",    StringType,  true)));

    val original_data:DataFrame = spark.read
      .options(Map("delimiter" -> "\t"))
      .schema(original_schema)
      .csv(path)
      .na.drop();

    // (~ 2:00 hour)
    // TODO: uncomment before delivery :)
    // val classifierTFIDF = trainClassifierTFIDF(original_data);


    spark.stop();
  }
}
