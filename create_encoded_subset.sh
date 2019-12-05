#!/bin/bash

hdfs dfs hdfs://localhost:9000/subsample_kindle.csv | python parser.py 1 > subset/subsample_kindle_ngram_1.csv
hdfs dfs hdfs://localhost:9000/subsample_kindle.csv | python parser.py 2 > subset/subsample_kindle_ngram_2.csv
hdfs dfs hdfs://localhost:9000/subsample_kindle.csv | python parser.py 3 > subset/subsample_kindle_ngram_3.csv
