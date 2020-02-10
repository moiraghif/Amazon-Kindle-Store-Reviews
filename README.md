# Text Analysis using Amazon reviews

Trying to guess number of stars on a subset of [amazon products](https://nijianmo.github.io/amazon/index.html) 
(containing only books and kindle store reviews) using natural text as input variable.
Special tanks to [Jianmo Ni](https://nijianmo.github.io/) for let us download his data.

# How to use

## Docker Creation

Execute [./docker_builder.sh](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/docker_builder.sh) script to create the docker enviorment, it will take time, otherwise use the docker-compose file to dowmload one already created and pushed to the docker hub. 
As soon as the docker starts it will automatically start hdfs and transfer the data to hadoop file system (using the [./hadoop-docker/start.sh](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/hadoop-docker/start.sh) script as entrypoint). 

## Data Preparation

After starting the docker enter in the /Project folder of the docker in which you will find this same folder copied and execute [./main.sh](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/main.sh) which will recall [clean.py](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/clean.py) and [parser.py](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/parser.py), these two files are passed to the hadoop ecosystem as mappers and the data is transformed. 

It takes around 1-2 hours depending your machine: tested with 8 cores and 12 cores processors, if you have less processor it might take more time.

## The jupyter notebooks

Now that the data is completely ready, just start the jupyter-notebook and open any of the jupyter notebook, the port 8888 should be mapped on your port 8888.

The [Regression_scala.ipynb](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/Regression_scala.ipynb) contains the spark code written in scala regarding the two classification tasks.

The [pyspark_notebook.ipynb](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/pyspark_notebook.ipynb) contains al the spark code written in python regarding all the other tasks, they are separated with header title.
