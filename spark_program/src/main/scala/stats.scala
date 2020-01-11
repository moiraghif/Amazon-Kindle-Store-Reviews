package statistics;

import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.types._;
import org.apache.spark.sql.functions._;
import org.apache.spark.ml.tuning.TrainValidationSplit;
import org.apache.spark.ml.feature.Binarizer;

import nlp.functions._;


object functions {

  def get_y_x(data : DataFrame, n : Integer) : (DataFrame, DataFrame) = {

    val df = get_ngrams(data, n, "words", "n_grams");

    val binarizer = new Binarizer()
      .setInputCol("rate")
      .setOutputCol("rate_bin")
      .setThreshold(3.5);
    val df_bin : DataFrame = binarizer.transform(df);

    (df_bin.select("rate_bin"), df_bin.select("n_grams"));
  }

}
