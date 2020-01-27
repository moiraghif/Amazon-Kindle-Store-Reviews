FROM ubuntu:16.04
MAINTAINER paperinik

ARG HADOOP_VER=3.2.1
ARG JAVA_VER=8

RUN apt update
RUN apt install -y openjdk-${JAVA_VER}-jdk openjdk-${JAVA_VER}-jre  openssh-client openssh-server python3 python3-pip wget

ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64
ENV JRE_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64/jre

#DOWNLOAD AND CONFIGURE HADOOP
RUN wget http://it.apache.contactlab.it/hadoop/common/hadoop-${HADOOP_VER}/hadoop-${HADOOP_VER}.tar.gz
RUN tar xvfz hadoop-${HADOOP_VER}.tar.gz &&  mv hadoop-${HADOOP_VER} /hadoop && rm hadoop-${HADOOP_VER}.tar.gz

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

#DONWNLOAD ANACONDA
RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh && \
    bash Anaconda3-2019.10-Linux-x86_64.sh -b -p /opt/conda && \
    rm Anaconda3-2019.10-Linux-x86_64.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

ENV PATH /opt/conda/bin:$PATH

#PYTHON LIBRARIES
RUN conda config --append channels conda-forge && \
    conda install -y \
      python=3.7.4 \
      # Math
      numpy=1.17.2 \
      pandas=0.25.1 \
      # Linguistics
      spacy=2.2.3 \
      nltk=3.4.5 \
      langdetect=1.0.7 &&\
      conda init

RUN pip install pycld2

# INSTALL SPACY FILES
RUN python -m spacy download en_core_web_sm


#INSTALL SPARK
#http://it.apache.contactlab.it/spark/spark-3.0.0-preview2/spark-3.0.0-preview2-bin-hadoop3.2.tgz



WORKDIR /

RUN mkdir Project && mkdir Project/spacy_model && mkdir Project/data
COPY ./ Project/
RUN python -c 'import nltk; nltk.download("stopwords", download_dir="./nltk/")' && cp ./nltk/corpora/stopwords/english Project/spacy_model/english_stopwords && rm -r ./nltk

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

RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ""
RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

COPY hadoop-docker/start.sh /
RUN chmod +x start.sh

ENV HADOOP_DATA "hdfs://localhost:9000/TextMining"


ENTRYPOINT ./start.sh
