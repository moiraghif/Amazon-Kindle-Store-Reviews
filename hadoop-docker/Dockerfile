FROM ubuntu:18.04
MAINTAINER paperinik

ARG HADOOP_VER=3.2.1
ARG JAVA_VER=8
ARG SPARK_VER=3.0.0
ARG SCALA_VER=2.12.10

RUN apt update
RUN apt install -y openjdk-${JAVA_VER}-jdk openjdk-${JAVA_VER}-jre \
                   openssh-client openssh-server \
                   python3 python3-pip wget curl

ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64
ENV JRE_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64/jre

#DOWNLOAD AND CONFIGURE HADOOP
RUN wget http://it.apache.contactlab.it/hadoop/common/hadoop-${HADOOP_VER}/hadoop-${HADOOP_VER}.tar.gz && \
    tar xvfz hadoop-${HADOOP_VER}.tar.gz && \
    mv hadoop-${HADOOP_VER} /hadoop && \
    rm hadoop-${HADOOP_VER}.tar.gz

ENV HADOOP_HOME /hadoop
ENV PATH $PATH:/$HADOOP_HOME/bin:/$HADOOP_HOME/sbin
ENV HADOOP_MAPRED_HOME $HADOOP_HOME 
ENV HADOOP_COMMON_HOME $HADOOP_HOME 

ENV HADOOP_HDFS_HOME $HADOOP_HOME 
ENV YARN_HOME $HADOOP_HOME 
ENV HADOOP_COMMON_LIB_NATIVE_DIR $HADOOP_HOME/lib/native
ENV HADOOP_INSTALL $HADOOP_HOME 

COPY hadoop-docker/configurations $HADOOP_HOME/etc/hadoop/

ENV HDFS_NAMENODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

RUN hdfs namenode -format

#PYTHON LIBRARIES
RUN python3 -m pip install --upgrade pip &&\
    python3 -m pip install \
      # Math
      numpy==1.17.2 \
      pandas==0.25.1 \
      #plotting
      matplotlib\
      seaborn\
      # Linguistics
      spacy==2.2.3 \
      nltk==3.4.5 \
      langdetect==1.0.7 \
      pycld2==0.41 \
      notebook\
      #scala kernel
      spylon-kernel

# INSTALL SPACY FILES
RUN python3 -m spacy download en_core_web_sm && \
    python3 -m spylon_kernel install


#INSTALL SPARK
RUN wget http://it.apache.contactlab.it/spark/spark-${SPARK_VER}-preview2/spark-${SPARK_VER}-preview2-bin-hadoop3.2.tgz && \
    tar xvfz spark-${SPARK_VER}-preview2-bin-hadoop3.2.tgz && \
    mv spark-${SPARK_VER}-preview2-bin-hadoop3.2 /spark && \
    rm spark-${SPARK_VER}-preview2-bin-hadoop3.2.tgz

RUN wget https://downloads.lightbend.com/scala/${SCALA_VER}/scala-${SCALA_VER}.deb && \
    dpkg -i scala-${SCALA_VER}.deb && \
    rm scala-${SCALA_VER}.deb

ENV SPARK_HOME /spark
ENV PATH $PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH $PYTHONPATH:$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.8.1-src.zip



RUN mkdir /Project

COPY ./ /Project/

RUN mkdir /Project/spacy_model && mkdir /Project/data 

WORKDIR /Project/

RUN python3 -c 'import nltk; nltk.download("stopwords", download_dir="./nltk/")' && \ 
    cp ./nltk/corpora/stopwords/english ./spacy_model/english_stopwords && \
    rm -r ./nltk

RUN python3 parser.py create_model

WORKDIR /

RUN wget -c "http://deepyeti.ucsd.edu/jianmo/amazon/categoryFiles/Kindle_Store.json.gz" \
     -O "Project/data/kindle_store.json.gz" && \
gzip -d "Project/data/kindle_store.json.gz"


# Hdfs ports
EXPOSE 50010 50020 50070 50075 50090
# Mapred ports
EXPOSE 19888
#Yarn ports
EXPOSE 8030 8031 8032 8033 8040 8042 8088
#Other ports
EXPOSE 49707 2122 9000
#SPARK PORTS
EXPOSE 4040 4041 8080
#4041 is a backup in case there are two spark sessions

RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -N "" && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

COPY hadoop-docker/start.sh /
RUN chmod +x start.sh

ENV HADOOP_DATA "hdfs://localhost:9000/TextMining"

WORKDIR /Project

ENTRYPOINT ../start.sh
