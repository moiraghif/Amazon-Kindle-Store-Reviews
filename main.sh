#!/bin/sh


HADOOP_DATA="hdfs://localhost:9000/TextMining"
start_dfs.sh
start_yarn.sh

echo "Waiting for Hadoop to be ready"

sleep 10

# create conda environment
conda create --name TextMining \
      python=3.7.4 \
      # Math
      numpy=1.17.2 \
      pandas=0.25.1 \
      # Linguistics
      nltk=3.4.5 \
      langdetect=1.0.7

conda activate TextMining
conda install --download-only nltk=3.4.5

# install NLTK files
python -c 'import nltk
nltk.download("stopwords", download_dir="./nltk/")
nltk.download("punkt",     download_dir="./nltk/")'


# download data and move them on HADOOP
mkdir "./data/"
wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" \
     -O "./data/kindle_store.json.gz"
gzip -d "./data/kindle_store.json.gz"

hadoop dfs -moveFromLocal \
       "./data/kindle_store.json" \
       $HADOOP_DATA/kindlestore.json

# clean all data removing non-English comments and missing values
# (~ 1.30h)
mapred streaming \
       -D mapreduce.job.name="Data cleaning" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/original_data/" \
       -output "$HADOOP_DATA/cleaned_data/" \
       -mapper "./clean_and_shuffle/clean.py" \
       -file "./clean_and_shuffle/clean.py"

# just shuffle the dataset (to improove sampling)
# (~ 5min)
mapred streaming \
       -D mapreduce.job.name="Shuffling data" \
       -D mapreduce.job.reduces=10  # this is parallelizable
       -input "$HADOOP_DATA/cleaned_data/" \
       -output "$HADOOP_DATA/shuffled_data/" \
       -file "./clean_and_shuffle/shuffle_mapper.py" \
       -mapper "./clean_and_shuffle/shuffle_mapper.py" \
       -file "./clean_and_shuffle/shuffle_reducer.py" \
       -reducer "./clean_and_shuffle/shuffle_reducer.py"

# extract a train set from shuffled data
# (~ 1min)
mapred streaming \
       -D mapreduce.job.name="Extract train set" \
       -D mapreduce.job.maps=1 \  # this is not parallelizable
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/shuffled_data/" \
       -output "$HADOOP_DATA/train_set/" \
       -file "./train_test_set/sampler_train.py" \
       -mapper "./train_test_set/sampler_train.py"

hdfs dfs -cat "$HADOOP_DATA/train_set/*" \
    | python "./train_test_set/train_set_index.py" \
             > "./train_test_set/train_set_index.csv"

# extract the test set: all remaining documents
# (~ 1min)
mapred streaming \
       -D mapreduce.job.name="Extract test set" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/shuffled_data/" \
       -output "$HADOOP_DATA/test_set/" \
       -file "./train_test_set/sampler_test.py" \
       -file "./train_test_set/train_set_index.csv" \
       -mapper "./train_test_set/sampler_test.py"

rm "./train_test_set/train_set_index.csv"


## TODO: spostare sull'HDFS
# bug: non si riesce a importare nltk come pacchetto all'interno di
# haddop

# create a vocaboulary from the subset
# (~ 10 min)
ln -rs "./tm_preprocessing.py" "./vocab/"

hdfs dfs -cat "$HADOOP_DATA/train_set/*" \
    | python "./vocab/mapper.py" 1 \
    | sort \
    | python "./vocab/reducer.py" \
             > "./vocab/vocab_1.csv"

hdfs dfs -cat "$HADOOP_DATA/train_set/*" \
    | python "./vocab/mapper.py" 3 \
    | sort \
    | python "./vocab/reducer.py" \
             > "./vocab/vocab_3.csv"


# encode documents using the vocaboulary
# (~ 20 min)
hdfs dfs -cat "$HADOOP_DATA/train_set/*" \
    | python "./parser.py" "./vocab/vocab_1.csv" "ntf" \
             > "./data/ngram_1_ntf.csv"

hdfs dfs -cat "$HADOOP_DATA/train_set/*" \
    | python "./parser.py" "./vocab/vocab_3.csv" "ntf" \
             > "./data/ngram_3_ntf.csv"

## DOCUMENTATION:
# data is now stored in a .csv file (~ 1GB) easilly readible by
# Pandas or R
# columns are stred in the following way:
# index words <RATE>
#
# RATE columns is <RATE> with < and > because there are no tokens with
# those signs (very good).
