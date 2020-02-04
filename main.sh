#!/bin/bash


# {{{ per @PK:
# potresti per favore mettere queste cose nell'init del docker? :)


# clean all data removing non-English comments and missing values
# (~ few minutes)
# >>> json file
# <<< product \t vote \t rate \t text
# sorted by product
 #need to test but seems ok now

export HADOOP_DATA="hdfs://localhost:9000/TextMining"

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


#mapred streaming \
#       -files "/Project/spacy_model" \
#       -D mapreduce.job.name="Clean data" \
#       -D mapreduce.job.reduces=0 \
#       -input "$HADOOP_DATA/cleaned_data/" \
#       -output "$HADOOP_DATA/lemma_tokens/" \
#       -mapper "parser.py" \
#       -file "/Project/parser.py"

cd /Project/spark_program


# SPARK

#No need now, use the notebook instead

# look how it is easy to compile it :D
#ln -s $SPARK_HOME/jars /Project/spark_program/lib
#sbt clean compile package

#$SPARK_HOME/bin/spark-submit /Project/spark_program/target/scala*/spark_program*.jar
