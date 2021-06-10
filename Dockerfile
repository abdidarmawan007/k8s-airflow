# take Airflow base image
FROM apache/airflow:2.0.2-python3.8

# add dags
COPY ./dags/ /opt/airflow/dags