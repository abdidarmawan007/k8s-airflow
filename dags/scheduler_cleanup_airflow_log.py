from datetime import datetime
import logging
import shutil
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from libraries.slack import slack_hook
from datetime import datetime, timedelta, date


default_args = {
    'owner': 'airflow',
    'depend_on_past': False,
    'start_date': datetime(2020, 12, 20),
    'email': ['andika.pramana@lemonilo.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'concurrency': 1,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'on_failure_callback': slack_hook
}

MAX_LOG_DAYS = 120
LOG_DIR = '/opt/airflow/logs/'

def find_old_logs():
    # Query old dag runs and build the log file paths to be deleted
    # Example log directory looks like this:
    # '/path/to/logs/dag_name/task_name/2021-01-11T12:25:00+00:00'
    sql = f"""
        SELECT '{LOG_DIR}' || dag_id || '/' || task_id || '/' || replace(execution_date::text, ' ', 'T') || ':00' AS log_dir
        FROM task_instance
        WHERE execution_date::DATE <= now()::DATE - INTERVAL '{MAX_LOG_DAYS} days'
        """

    src_pg = PostgresHook(postgres_conn_id='airflow_db')
    conn = src_pg.get_conn()
    logging.info("Fetching old logs to purge...")

    with conn.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        logging.info(f"Found {len(rows)} log directories to delete...")
    
    for row in rows:
        delete_log_dir(row[0])

def delete_log_dir(log_dir):
    try:
        # Recursively delete the log directory and its log contents (e.g, 1.log, 2.log, etc)
        shutil.rmtree(log_dir)
        #logging.info(f"Deleted directory and log contents: {log_dir}")
    except OSError as e:
        pass
        #logging.info(f"Unable to delete: {e.filename} - {e.strerror}")


dag = DAG('airflow_log_cleanup', default_args=default_args, catchup=False, schedule_interval='0 0 * * *')

log_cleanup_op = PythonOperator(
        task_id="delete_old_logs",
        python_callable=find_old_logs,
        dag=dag,
    )

log_cleanup_op
