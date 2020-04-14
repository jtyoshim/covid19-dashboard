FROM ubuntu:18.04
WORKDIR .
RUN mkdir app
RUN mkdir ./app/dashboard
COPY . ./app/dashboard
RUN apt-get update -y &&  \
    apt-get install -y --no-install-recommends python3-pip python3-setuptools
RUN pip3 install -U plotly
RUN pip3 install dash dash-renderer dash-html-components dash-core-components folium geopandas
CMD ["python3", "./app/dashboard/dashboard.py"]