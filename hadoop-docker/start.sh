service ssh start

sleep 5 #wait for ssh to start
#conda activate

start-dfs.sh
start-yarn.sh

hdfs dfs -mkdir "$HADOOP_DATA" && \
   hdfs dfs -mkdir "$HADOOP_DATA/original_data" && \
   hdfs dfs -moveFromLocal \
     "Project/data/kindle_store.json" \
     "$HADOOP_DATA/original_data/kindlestore.json"

bash
