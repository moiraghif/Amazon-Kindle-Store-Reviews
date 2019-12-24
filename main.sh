#!/bin/bash


HADOOP_DATA="hdfs://localhost:9000/TextMining"
start-dfs.sh
start-yarn.sh

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

mkdir "./spacy_models"
python "./parser.py" create_model


# download NLTK stopwords
python -c 'import nltk; nltk.download("stopwords", download_dir="./nltk/")'
cp "./nltk/corpora/stopwords/english" "./english_stopwords"
rm -r "./nltk"


# download data and move them on HADOOP
mkdir "./data/"
wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" \
     -O "./data/kindle_store.json.gz"
gzip -d "./data/kindle_store.json.gz"

hdfs dfs -mkdir "$HADOOP_DATA"
hdfs dfs -mkdir "$HADOOP_DATA/original_data"
hdfs dfs -moveFromLocal \
     "./data/kindle_store.json" \
     "$HADOOP_DATA/original_data/kindlestore.json"

# clean all data removing non-English comments and missing values
#
# >>> json file
# <<< product \t vote \t rate \t text (sorted by product)
#
mapred streaming \
       -D mapreduce.job.name="Data cleaning" \
       -input "$HADOOP_DATA/original_data/" \
       -output "$HADOOP_DATA/cleaned_data/" \
       -file "./clean_and_shuffle/clean.py" \
       -mapper "./clean_and_shuffle/clean.py"


for n in 1 3  # monograms and trigrams
do
    # extract n-grams from the whole collection
    #
    # >>> product \t vote \t rate \t text
    # <<< product \t vote \t rate \t ngrams
    #
    mapred streaming \
           -files "./spacy_models" \
           -D mapreduce.job.name="Extract $n-grams" \
           -D mapreduce.job.reduces=0 \
           -input "$HADOOP_DATA/cleaned_data/" \
           -output "$HADOOP_DATA/$n_grams/" \
           -file "./english_stopwords" \
           -file "./parser.py" \
           -mapper "./parser.py extract_ngrams $n"

    # extract vocaboulary from the n-grams list
    #
    # >>> product \t vote \t rate \t ngrams
    # <<< vocaboulary
    #
    mapred streaming \
           -D mapreduce.job.name="Extract vocaboulary for $n-grams" \
           -input "$HADOOP_DATA/$n_grams/" \
           -output "$HADOOP_DATA/$n_vocab/" \
           -file "./vocab/mapper.py" \
           -mapper "./vocab/mapper.py" \
           -file "./vocab/reducer.py" \
           -reducer "./vocab/reducer.py"

    hdfs dfs -cat "$HADOOP_DATA/$n_vocab/*" \
         > "./vocab_$n.csv"

    # encode documents using ntf encoding
    #
    # >>> product \t vote \t rate \t ngrams
    # <<< product \t vote \t rate \t encoding
    #
    mapred streaming \
            -files "./spacy_models" \
            -D mapreduce.job.name="Encode documents for $n-grams" \
            -D mapreduce.job.reduces=0 \
            -input "$HADOOP_DATA/$n_grams/" \
            -output "$HADOOP_DATA/$n_grams_ntf" \
            -file "./english_stopwords" \
            -file "./vocab_$n.csv" \
            -file "./parser.py" \
            -mapper "./parser.py encode_ngrams ntf vocab_$n.csv"

    # just shuffle the dataset (to improove sampling)
    #
    # >>> product \t vote \t rate \t encoding
    # <<< i \t rate \t text
    #
    mapred streaming \
           -D mapreduce.job.name="Shuffling data for $n-grams" \
           -D mapreduce.job.reduces=10  \
           -input "$HADOOP_DATA/$n_grams_ntf/" \
           -output "$HADOOP_DATA/$n_grams_ntf_shuff/" \
           -file "./clean_and_shuffle/shuffle_mapper.py" \
           -mapper "./clean_and_shuffle/shuffle_mapper.py" \
           -file "./clean_and_shuffle/shuffle_reducer.py" \
           -reducer "./clean_and_shuffle/shuffle_reducer.py"

    # extract a train set from shuffled data
    #
    # i \t rate \t text
    #
    mapred streaming \
           -D mapreduce.job.name="Extract train set for $n-grams" \
           -D mapreduce.job.maps=1 \
           -D mapreduce.job.reduces=0 \
           -input "$HADOOP_DATA/$n_grams_ntf_shuff/" \
           -output "$HADOOP_DATA/$n_grams_train/" \
           -file "./train_test_set/sampler_train.py" \
           -mapper "./train_test_set/sampler_train.py"
    
    hdfs dfs -cat "$HADOOP_DATA/$n_grams_train/*" \
        | python "./train_test_set/train_set_index.py" \
                 > "./train_test_set/$n_grams_train.csv"
    
    # extract the test set: all remaining documents
    #
    # i \t rate \t text
    #
    mapred streaming \
           -D mapreduce.job.name="Extract test set for $n-grams" \
           -D mapreduce.job.reduces=0 \
           -input "$HADOOP_DATA/$n_grams_ntf_shuff/" \
           -output "$HADOOP_DATA/$n_grams_test/" \
           -file "./train_test_set/sampler_test.py" \
           -file "./train_test_set/$n_grams_train.csv" \
           -mapper "./train_test_set/sampler_test.py"

done

# encode documents using RoBERTa
#
# >>> product \t vote \t rate \t text
# <<< product \t vote \t rate \t encoding
#
mapred streaming \
       -files "./spacy_models" \
       -D mapreduce.job.name="Encoding data with RoBERTa" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/cleaned_data/" \
       -output "$HADOOP_DATA/RoBERTa/" \
       -file "./english_stopwords" \
       -file "./parser.py" \
       -mapper "./parser.py encode_text roberta"

mapred streaming \
           -D mapreduce.job.name="Shuffling data for RoBERTa" \
           -D mapreduce.job.reduces=10  \
           -input "$HADOOP_DATA/RoBERTa/" \
           -output "$HADOOP_DATA/RoBERTa_shuff/" \
           -file "./clean_and_shuffle/shuffle_mapper.py" \
           -mapper "./clean_and_shuffle/shuffle_mapper.py" \
           -file "./clean_and_shuffle/shuffle_reducer.py" \
           -reducer "./clean_and_shuffle/shuffle_reducer.py"

mapred streaming \
       -D mapreduce.job.name="Extract train set for RoBERTa" \
       -D mapreduce.job.maps=1 \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/RoBERTa_shuff/" \
       -output "$HADOOP_DATA/RoBERTa_train/" \
       -file "./train_test_set/sampler_train.py" \
       -mapper "./train_test_set/sampler_train.py"

hdfs dfs -cat "$HADOOP_DATA/RoBERTa_train/*" \
    | python "./train_test_set/train_set_index.py" \
             > "./train_test_set/RoBERTa_train.csv"

mapred streaming \
       -D mapreduce.job.name="Extract test set for RoBERTa" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/RoBERTa_shuff/" \
       -output "$HADOOP_DATA/RoBERTa_test/" \
       -file "./train_test_set/sampler_test.py" \
       -file "./train_test_set/RoBERTa_train.csv" \
       -mapper "./train_test_set/sampler_test.py"


## DOCUMENTATION:
# data is now stored in a .csv file easilly readible by Pandas or R
# columns are stred in the following way:
# index, encoding, <RATE>
