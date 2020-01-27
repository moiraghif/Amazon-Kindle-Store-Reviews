#!/bin/bash


# {{{ per @PK:
# potresti per favore mettere queste cose nell'init del docker? :)


# clean all data removing non-English comments and missing values
# (~ few minutes)
# >>> json file
# <<< product \t vote \t rate \t text
# sorted by product
 #need to test but seems ok now
mapred streaming \
       -files "/Project/clean.py" \
       -D mapreduce.job.name="Normalize data & Remove useless reviews" \
       -input "$HADOOP_DATA/original_data/" \
       -output "$HADOOP_DATA/cleaned_data/" \
       -mapper "clean.py"


# extract n-grams from the whole collection
# (~ 30 min)
# >>> product \t vote \t rate \t text
# <<< product \t vote \t rate \t ngrams
# sorted by product
mapred streaming \
       -files "/Project/spacy_model" \
       -D mapreduce.job.name="Clean data" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/cleaned_data/" \
       -output "$HADOOP_DATA/tokens/" \
       -mapper "parser.py" \
       -file "/Project/parser.py"

cd spark_program


# SPARK

# look how it is easy to compile it :D
mkdir lib/
ln -s $SPARK_HOME/jars ./lib
sbt clean compile package

$SPARK_HOME/bin/spark-submit target/scala*/spark_program*.jar
