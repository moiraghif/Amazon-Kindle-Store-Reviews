docker build -t hadoop -f hadoop-docker/Dockerfile .
docker run -it -p 8088:8088 4040:4040 hadoop

#do what you want to do in the docker shell now
#for example the following commands:

#mapred streaming \ #need to test but seems ok now
#  -files "/Project/clean.py" \
#  -D mapreduce.job.name="Normalize data & Remove useless reviews" \
#  -input "$HADOOP_DATA/original_data/" \
#  -output "$HADOOP_DATA/cleaned_data/" \
#  -mapper "clean.py"
