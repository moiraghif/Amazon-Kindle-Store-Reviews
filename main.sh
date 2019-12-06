#!/bin/sh


## REQUIRED FILES:
# ./main.sh
# ./tm_preprocessing.py
# ./parser.py
# ./train_test_set/sampler_mapper.py
# ./train_test_set/sampler_reducer.py
# ./train_test_set/train_mapper.py
# ./train_test_set/test_mapper.py
# ./vocab/mapper.py
# ./vocab/reducer.py

HADOOP_DATA="hdfs://localhost:9000"
$HADOOP_HOME/sbin/start_all.sh

# download data and move them on HADOOP
mkdir "./data/"
wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" \
     -O "./data/kindle_store.json.gz"
gzip -d "./data/kindle_store.json.gz"

hadoop dfs -moveFromLocal \
       "./data/kindle_store.json" \
       $HADOOP_DATA/kindlestore.json

# extract a stratified subset of data (memory expensive, sorry) as train set
hdfs dfs -cat $HADOOP_DATA/kindlestore.json \
    | python "./train_test_set/sampler_mapper.py" \
    | shuf \
    | python "./train_test_set/sampler_reducer.py" \
    | hdfs dfs -appendToFile - $HADOOP_DATA/train_set.csv

# store documents sequential number (= index) on a file
hdfs dfs -cat $HADOOP_DATA/train_set.csv \
    | python "./train_test_set/train_mapper.py" \
             > "./train_test_set/train_set_index.csv"

# all other documents are considered as test set
hdfs dfs -cat $HADOOP_DATA/kindlestore.json \
    | python "./train_test_set/test_mapper.py" \
    | hdfs dfs -appendToFile - $HADOOP_DATA/test_set.csv


# create a vocaboulary from the subset (~ 10 min)
ln -rs "./tm_preprocessing.py" ./vocab/

hdfs dfs -cat $HADOOP_DATA/train_set.csv \
    | python "./vocab/mapper.py" 1 \
    | sort \
    | python "./vocab/reducer.py" \
             > "./vocab/vocab_1.csv"

hdfs dfs -cat $HADOOP_DATA/train_set.csv \
    | python "./vocab/mapper.py" 3 \
    | sort \
    | python "./vocab/reducer.py" \
             > "./vocab/vocab_3.csv"


# encode documents using the vocaboulary (~ 20 min)
hdfs dfs -cat $HADOOP_DATA/train_set.csv \
    | python "./parser.py" "vocab/vocab_1.csv" "ntf" \
             > "./data/ngram_1_ntf.csv"

hdfs dfs -cat $HADOOP_DATA/train_set.csv \
    | python "./parser.py" "vocab/vocab_3.csv" "ntf" \
             > "./data/ngram_3_ntf.csv"

## DOCUMENTATION:
# data is now stored in a .csv file (~ 1GB) easilly readible by
# Pandas or R
# columns are stred in the following way:
# index words <RATE>
#
# RATE columns is <RATE> with < and > because there are no tokens with
# those signs (very good).
