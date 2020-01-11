package main;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.types._;
import org.apache.spark.sql.functions._;
import org.apache.spark.rdd.RDD;
import org.apache.spark.ml.feature.NGram;
import org.apache.spark.ml.feature.{Tokenizer, RegexTokenizer};
import org.apache.spark.ml.feature.{HashingTF, IDF};

import nlp.functions._;
import statistics.functions._;


object TextMining {

  def main(args: Array[String]) {

    // initialize Spark
    val spark: SparkSession = SparkSession.builder()
      .appName("TextMining with Spark & Scala")
      .getOrCreate();
    spark.sparkContext.setLogLevel("ERROR");


    // get input data and split text into tokens
    val path: String = "hdfs://localhost:9000/TextMining/tokens/";

    val original_schema = new StructType(Array(
      StructField("product", StringType,  true),
      StructField("votes",   IntegerType, true),
      StructField("rate",    DoubleType, true),
      StructField("text",    StringType,  true)));

    val original_data:DataFrame = spark.read
      .options(Map("delimiter" -> "\t"))
      .schema(original_schema)
      .csv(path);

    val data : DataFrame = get_tokens(original_data.na.drop(), "text", "words");

    val (y2, x2) = get_y_x(data, 2);

    // print results
    println(x2.show());
    println(y2.show());

    spark.stop();
  }
}
