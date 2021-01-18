FROM centos:centos7
RUN yum update -y
RUN yum install -y epel-release \
    which \
    python3 \
    python3-devel \
    gcc \
    libXau libXmu libGLU \
    postgresql-libs \
    postgresql-devel
RUN mkdir -p /project/code/simserv \
     /project/code/simserv/data \
     /project/code/simserv/sitecluster/bin \
     /project/code/simserv/ads/
WORKDIR /project/code/simserv
COPY ads_2020_update2.0_linux_x64.tar /project/code/simserv/ 
RUN tar -xvf ads_2020_update2.0_linux_x64.tar \
    && ./SETUP.SH -i silent -DUSER_INSTALL_DIR=/project/code/simserv/ads/ \
    && rm -rf linux_x86_64 dongle_sup SETUP.SH ads_2020_update2.0_linux_x64.tar
RUN python3 -m venv /project/code/simserv
COPY *.whl /project/code/simserv/
ENV LC_ALL=en_US.UTF8 \
    LANG=en_US.UTF8
RUN /project/code/simserv/bin/python -m pip install --no-cache --upgrade pip setuptools wheel \
    psycopg2 \
    -f /project/code/simserv keysight-simserv \
    && rm -f keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl
COPY sitecluster sitecluster.py /project/code/simserv/sitecluster/bin/
COPY .env /project/code/simserv/
CMD ["/project/code/simserv/bin/simserv", "run"]         
