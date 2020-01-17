package statistics;

import org.apache.spark.sql.DataFrame;
import org.apache.spark.sql.types._;
import org.apache.spark.sql.functions._;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.Model;
import org.apache.spark.ml.classification.LogisticRegression;
import org.apache.spark.ml.evaluation.BinaryClassificationEvaluator;
import org.apache.spark.ml.feature.Binarizer;
import org.apache.spark.ml.feature.{RegexTokenizer, NGram};
import org.apache.spark.ml.feature.{HashingTF, IDF};
import org.apache.spark.ml.tuning.{CrossValidator, ParamGridBuilder};


object functions {

  def trainClassifierTFIDF(data : DataFrame) : Model[_] = {

    // binarize target column
    val binarizer = new Binarizer()
      .setInputCol("rate")
      .setOutputCol("label")
      .setThreshold(3.5);

    // get n-grams
    val tokenizer = new RegexTokenizer()
      .setInputCol("text")
      .setOutputCol("tokens")
      .setPattern("\\W");
    val ngrams = new NGram()
      .setInputCol(tokenizer.getOutputCol)
      .setOutputCol("n-grams");

    // calc tf-idf 
    val tf = new HashingTF()
      .setInputCol(ngrams.getOutputCol)
      .setOutputCol("tf");
    val idf = new IDF()
      .setInputCol(tf.getOutputCol)
      .setOutputCol("tf-idf")
      .setMinDocFreq(3);

    // build the classifier
    val classifierMod = new LogisticRegression()
      .setMaxIter(10)
      .setFeaturesCol(idf.getOutputCol)
      .setLabelCol(binarizer.getOutputCol);

    // this is the pipeline that data follows to be evaluated
    val pipeline = new Pipeline()
      .setStages(Array(binarizer, tokenizer, ngrams, tf, idf, classifierMod));

    // a little of optimization: try different hyperparameters
    val paramGrid = new ParamGridBuilder()
      .addGrid(classifierMod.regParam, Array(0.01, 0.05, 0.1))
      .addGrid(ngrams.n, Array(1, 2, 3))
      .build();

    // do it with a cross validation on the train set (3 folds)
    val cv = new CrossValidator()
      .setEstimator(pipeline)
      .setEvaluator(new BinaryClassificationEvaluator)
      .setEstimatorParamMaps(paramGrid)
      .setNumFolds(3);

    // ok, start the train
    print("Training... ");
    val model = cv.fit(data);
    println("done!");

    // print results
    for (i <- 0 until model.avgMetrics.size) {
      println("\n\n");
      println(model.getEstimatorParamMaps(i));
      println(model.avgMetrics(i));
    }

    model.bestModel;
  }

}
