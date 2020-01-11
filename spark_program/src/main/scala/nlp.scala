package nlp;

import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.functions._;
import org.apache.spark.ml.feature.NGram;
import org.apache.spark.ml.feature.RegexTokenizer;
import org.apache.spark.ml.feature.{HashingTF, IDF};

object functions {

  def get_tokens(df: DataFrame, in: String, out: String) : DataFrame = {
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
}
