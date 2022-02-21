# take Airflow base image
FROM apache/airflow:2.0.2-python3.8

# install additional pip packages
RUN pip install python-slugify~=4.0.1 && \
    pip install python-graphql-client~=0.4.3 && \
    pip install --upgrade google-cloud-bigquery

# add dags
COPY ./dags/ /opt/airflow/dags
