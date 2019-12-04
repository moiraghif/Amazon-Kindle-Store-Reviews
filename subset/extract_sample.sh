#!/bin/bash

hdfs dfs -cat hdfs://localhost:9000/kindlestore.json | python mapper.py | shuf | python reducer.py > subsample_kindle.csv
