#!/bin/bash

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
# (~ 30 min to ~1 hour)
# sorted by product
mapred streaming \
       -files "/Project/spacy_model" \
       -D mapreduce.job.name="Clean data" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/cleaned_data/" \
       -output "$HADOOP_DATA/tokens/" \
       -mapper "parser.py" \
       -file "/Project/parser.py"

