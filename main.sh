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
      spacy=2.2.3 \
      nltk=3.4.5 \
      langdetect=1.0.7

conda activate TextMining


# install SPACY files
python -m spacy download en_core_web_sm
python -m spacy download en_trf_robertabase_lg


# download NLTK stopwords
python -c 'import nltk; nltk.download("stopwords", download_dir="./nltk/")'
cp "./nltk/corpora/stopwords/english" "./english_stopwords"
rm -r "./nltk"


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

# create a vocaboulary from the subset
# (~ 40 min)
mkdir "./spacy_models"
python "parser.py" create_model


## TODO: per ottimizzare si potrebbe tenere una copia in cache degli
# n-grammi di ogni documento

mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Extract vocab with mono-grams" \
       -input "$HADOOP_DATA/train_set" \
       -output "$HADOOP_DATA/1" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -mapper "./parser.py extract_ngrams 1" \
       -file "./vocab/reducer.py" \
       -reducer "./vocab/reducer.py"

hdfs dfs -cat "$HADOOP_DATA/vocab_1/*" > "./vocab_1.csv"


mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Extract vocab with tri-grams" \
       -input "$HADOOP_DATA/train_set" \
       -output "$HADOOP_DATA/vocab_3" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -mapper "./parser.py extract_ngrams 3" \
       -file "./vocab/reducer.py" \
       -reducer "./vocab/reducer.py"

hdfs dfs -cat "$HADOOP_DATA/vocab_3/*" > "./vocab_3.csv"


# encode documents using the vocaboulary
# (~ 20 min)
mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Encoding train_set with monograms and ntf" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/train_set" \
       -output "$HADOOP_DATA/train_set_1gram_ntf" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -file "./vocab_1.csv" \
       -mapper "./parser.py encode ntf ./vocab_1.csv"


mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Encoding train_set with trigrams and ntf" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/train_set" \
       -output "$HADOOP_DATA/train_set_3gram_ntf" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -file "./vocab_1.csv" \
       -mapper "./parser.py encode ntf ./vocab_3.csv"


mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Encoding train_set with RoBERTa" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/train_set" \
       -output "$HADOOP_DATA/train_set_roberta" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -file "./vocab_1.csv" \
       -mapper "./parser.py encode roberta"



## DOCUMENTATION:
# data is now stored in a .csv file (~ 1GB) easilly readible by
# Pandas or R
# columns are stred in the following way:
# index, encoding, <RATE>
