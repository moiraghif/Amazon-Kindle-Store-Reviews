package main;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.types._;
import org.apache.spark.sql.functions._;
import org.apache.spark.rdd.RDD;
import org.apache.spark.ml.feature.NGram;
import org.apache.spark.ml.feature.{Tokenizer, RegexTokenizer};
import org.apache.spark.ml.feature.{HashingTF, IDF};


object TextMining {

  def get_tokens(df: DataFrame, in: String, out: String): DataFrame = {
    val regexTokenizer = new RegexTokenizer()
      .setInputCol(in)
      .setOutputCol(out)
      .setPattern("\\W");

    regexTokenizer.transform(df);
  }

  def get_ngrams(df: DataFrame, n:Int, in: String, out: String): DataFrame = {
    val ngram = new NGram()
      .setN(n)
      .setInputCol(in)
      .setOutputCol(out);

    ngram.transform(df);
  }

  def calc_tfidf(df: DataFrame, in: String): DataFrame = {
    val tfModel = new HashingTF()
      .setInputCol(in)
      .setOutputCol("tf");
    
    val idfModel = new IDF()
      .setInputCol("tf")
      .setOutputCol("tfidf");

    val tf = tfModel.transform(df);

    idfModel.fit(tf).transform(tf);
  }

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
      StructField("rate",    IntegerType, true),
      StructField("text",    StringType,  true)));

    val original_data:DataFrame = spark.read
      .options(Map("delimiter" -> "\t"))
      .schema(original_schema)
      .csv(path);


    val df = get_tokens(original_data.na.drop(), "text", "words")
    val df2 = get_ngrams(df, 2, "words", "2grams");

    // calc tfidf
    val df2_tfidf = calc_tfidf(df2, "2grams");

    // print results
    println("\n\n");
    println(df2_tfidf.show());
    println("\n\n");

    spark.stop();
  }
}
