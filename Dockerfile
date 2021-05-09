ARG ver
ARG HTTP_PROXY
FROM centos:${ver}
MAINTAINER devopsteam \
email devops.com \
loc chennai
ENV JAVA_HOM=/opt/java
ENV HTTP_PROXY
RUN mkdi chmod yum
ONBUILD RUN script.bash
COPY httpd.conf /etc/httpd/conf/httpd.conf
ADD url.pkg /opt/local/tomcat
COPY start.sh /opt
RUN chmod a+x /opt/start.sh
LABEL env=acc \
      type=web \
RUN ./script.bash
HEALTHCHECK curl http://localhost:80 || exit 1
CMD [ "/opt/start.sh" ]