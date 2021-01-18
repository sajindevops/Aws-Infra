FROM centos:centos7
RUN yum update -y
RUN mkdir -p /opt/ads
WORKDIR /opt/ads/
COPY ads_2020_update2.0_linux_x64.tar /opt/ads 
RUN tar -xvf ads_2020_update2.0_linux_x64.tar \
    && ./SETUP.SH -i silent -DUSER_INSTALL_DIR=/opt/ads/ \
    && rm -rf linux_x86_64 dongle_sup SETUP.SH ads_2020_update2.0_linux_x64.tar
RUN chmod a+x -R /opt/ads/bin
RUN chmod a+x -R /opt/ads/fem
CMD ["/bin/bash"] 
