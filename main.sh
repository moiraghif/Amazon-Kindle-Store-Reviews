#!/bin/sh


## REQUIRED FILES:
# ./main.sh
# ./downloader.sh
# ./tm_preprocessing.py
# ./parser.py
# ./subset/mapper.sh
# ./subset/reducer.sh
# ./creazione\ vocabolario/mapper.py
# ./creazione\ vocabolario/reducer.py


$HADOOP_HOME/sbin/start_all.sh

# download data and move on HADOOP
bash downloader.sh
hadoop dfs -moveFromLocal ./data/kindle_store.json hdfs://localhost:9000/kindlestore.json

# extract a stratified subset of data (memory expensive, sorry)
hdfs dfs -cat hdfs://localhost:9000/kindlestore.json | python ./subset/mapper.py | shuf | python ./subset/reducer.py > hdfs://localhost:9000/subsample_kindle.csv

# create a vocaboulary from the subset
ln -rs ./tm_preprocessing.py ./creazione\ vocabolario/
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python ./creazione\ vocabolario/mapper.py 1 | sort | python ./creazione\ vocabolario/reducer.py > creazione\ vocabolario/vocab_1.csv
# hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python ./creazione\ vocabolario/mapper.py 2 | sort | python ./creazione\ vocabolario/reducer.py > creazione\ vocabolario/vocab_2.csv
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python ./creazione\ vocabolario/mapper.py 3 | sort | python ./creazione\ vocabolario/reducer.py > creazione\ vocabolario/vocab_3.csv

# encode documents using the vocaboulary
mkdir dataset
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python ./parser.py creazione\ vocabolario/vocab_1.csv ntf > dataset/ngram_1_ntf.csv
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python ./parser.py creazione\ vocabolario/vocab_3.csv ntf > dataset/ngram_3_ntf.csv
