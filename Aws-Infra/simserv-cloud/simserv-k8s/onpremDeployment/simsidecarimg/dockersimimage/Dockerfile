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
     /opt/ads/
WORKDIR /project/code/simserv
RUN python3 -m venv /project/code/simserv
COPY *.whl /project/code/simserv/
ENV LC_ALL=en_US.UTF8 \
    LANG=en_US.UTF8 \
    HPEESOF_DIRS=/opt/ads/
RUN /project/code/simserv/bin/python -m pip install --no-cache --upgrade pip setuptools wheel \
    psycopg2 \
    -f /project/code/simserv keysight-simserv \
    && rm -f keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl
COPY sitecluster sitecluster.py /project/code/simserv/sitecluster/bin/
COPY .env /project/code/simserv/
CMD ["/project/code/simserv/bin/simserv", "run"]         
