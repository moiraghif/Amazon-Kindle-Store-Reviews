FROM ubuntu:16.04
MAINTAINER paperinik

ARG HADOOP_VER=3.2.1
ARG JAVA_VER=8

RUN apt update
RUN apt install -y openjdk-${JAVA_VER}-jdk openjdk-${JAVA_VER}-jre  openssh-client openssh-server python3 python3-pip wget

ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64
ENV JRE_HOME=/usr/lib/jvm/java-${JAVA_VER}-openjdk-amd64/jre

#DOWNLOAD HADOOP
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

COPY configurations $HADOOP_HOME/etc/hadoop/
#COPY conf/hadoop-env.cmd $HADOOP_HOME/etc/hadoop/

ENV HDFS_NAMENODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

RUN hdfs namenode -format

#DONWNLOAD ANACONDA
#RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
#RUN bash Anaconda3-2019.10-Linux-x86_64.sh

WORKDIR /

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

COPY start.sh /
RUN chmod +x ./start.sh

ENTRYPOINT ./start.sh
