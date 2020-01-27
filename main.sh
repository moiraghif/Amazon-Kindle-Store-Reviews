#!/bin/bash


# {{{ per @PK:
# potresti per favore mettere queste cose nell'init del docker? :)
export HADOOP_DATA="hdfs://localhost:9000/TextMining"
# export HADOOP_HOME=/path/to/hadoop
# export SPARK_HOME=/path/to/spark

conda create --name TextMining \ #done
      python=3.7.4 \
      # Math
      numpy=1.17.2 \
      pandas=0.25.1 \
      # Linguistics
      spacy=2.2.3 \
      nltk=3.4.5 \
      langdetect=1.0.7

conda activate TextMining #not needed it's already a virtual env 
# }}}


# install SPACY files
python -m spacy download en_core_web_sm #done

mkdir "./spacy_models" #done
python "./parser.py" "create_model" #done


# download NLTK stopwords
python -c 'import nltk; nltk.download("stopwords", download_dir="./nltk/")' #done
cp "./nltk/corpora/stopwords/english" "./spacy_model/english_stopwords" #done
rm -r "./nltk" #done


# download data and move them on HADOOP
mkdir "./data/"  #done
wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" \
     -O "./data/kindle_store.json.gz" #done
gzip -d "./data/kindle_store.json.gz" #done


hdfs dfs -mkdir "$HADOOP_DATA" #done
hdfs dfs -mkdir "$HADOOP_DATA/original_data" #done
hdfs dfs -moveFromLocal \ #done
     "./data/kindle_store.json" \
     "$HADOOP_DATA/original_data/kindlestore.json"


# clean all data removing non-English comments and missing values
# (~ 1 hour)
# >>> json file
# <<< product \t vote \t rate \t text
# sorted by product
mapred streaming \ #need to test but seems ok now
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
       -files "./spacy_models", "./parser.py" \
       -D mapreduce.job.name="Clean data" \
       -D mapreduce.job.reduces=0 \
       -input "$HADOOP_DATA/cleaned_data/" \
       -output "$HADOOP_DATA/tokens/" \
       -mapper "./parser.py extract_tokens"


cd spark_program


# SPARK

# look how it is easy to compile it :D
rmdir lib/
ln -s $SPARK_HOME/jars ./lib
sbt clean compile package

$SPARK_HOME/bin/spark-submit target/scala*/spark_program*.jar
