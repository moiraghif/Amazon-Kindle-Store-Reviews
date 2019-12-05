#!/bin/sh

mkdir "./data/"
wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" -O "./data/kindle_store.json.gz"
gzip -d "./data/kindle_store.json.gz"
