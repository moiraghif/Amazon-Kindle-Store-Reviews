#!/bin/bash

hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python mapper.py 1 | sort | python reducer.py  > vocab_1.csv
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python mapper.py 2 | sort | python reducer.py  > vocab_2.csv
hdfs dfs -cat hdfs://localhost:9000/subsample_kindle.csv | python mapper.py 3 | sort | python reducer.py  > vocab_3.csv
