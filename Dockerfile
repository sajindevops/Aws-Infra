ARG ver
ARG HTTP_PROXY
FROM centos:${ver}
MAINTAINER devopsteam \
email devops.com \
loc chennai
ENV JAVA_HOM=/opt/java
ENV HTTP_PROXY
RUN mkdi chmod yum
COPY httpd.conf /etc/httpd/conf/httpd.conf
ADD url.pkg /opt/local/tomcat
