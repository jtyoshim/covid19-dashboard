FROM ubuntu:18.04
WORKDIR .
COPY . ./
RUN apt-get update -y &&  \
    apt-get install -y --no-install-recommends python3-pip python3-setuptools
RUN pip3 install -U plotly
RUN pip3 install dash dash-renderer dash-html-components dash-core-components
CMD ["python3", "./dashboard.py"]