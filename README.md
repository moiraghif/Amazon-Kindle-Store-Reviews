# Text Analysis using Amazon reviews

Analysis of reviews from [Amazon Kindle Store](https://nijianmo.github.io/amazon/index.html) 
Special tanks to [Jianmo Ni](https://nijianmo.github.io/) for let us download his data.

## Presenation on Prezi: [Click Here](https://prezi.com/p/3ahifvn7zbad/)


# How to use

## Docker Creation

#### **To create docker without the docker hub (might take a lot of time):**

Execute [`./docker_builder.sh`](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/docker_builder.sh): this script will create the docker environment; it will take time, otherwise use the docker-compose file to download one already created and pushed to the docker hub. 
As soon as the docker starts, it will automatically start HDFS daemon and transfer the data into Hadoop File System (using the [./hadoop-docker/start.sh](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/hadoop-docker/start.sh) script as entry point). 

#### **To use the docker image already created and uploaded to docker hub(it's faster):**

Run anywhere:
`docker run -it -p 8888:8888 -p 4040:4040 pkasela/amazon_review_hadoop_spark:final` 
It contains the code folder and everything necessary for it to work.


## Data Preparation

After starting the docker, enter in the `/Project` folder of the docker, in which you will find this repository, and execute [`./main.sh`](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/main.sh) which will recall [clean.py](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/clean.py) and [parser.py](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/parser.py): these two files are passed to Hadoop as mappers to transform data.

It takes around 1 or 2 hours (depending on hardware): it has been tested with 8 cores and 12 cores processors, if you have less computational power it might take more time.

## The jupyter notebooks

Now that data is ready, just start `jupyter-notebook --ip 0.0.0.0 --allow-root` and open any of the Jupyter Notebook: docker's port 8888 should be mapped on your port 8888.

The [`Regression_scala.ipynb`](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/Regression_scala.ipynb) contains the Spark code written in Scala regarding the two classification tasks.
The [`pyspark_notebook.ipynb`](https://github.com/moiraghif/Amazon-Rating-Prediction/blob/master/pyspark_notebook.ipynb) instead contains all the Spark code written in Python regarding all the other tasks.

# About Us

| Who are we       | Roll No.        |
|------------------|-----------------|
| Federico Moiraghi| 799735          |
| Pranav Kasela    | 846965          |
| Roberto Berlucchi| 847939          |
    
