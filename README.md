## Install Official Airflow chart using helm 3 "Google Kubernetes Engine"

## Add repo airflow
```
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm repo list
NAME          	URL                       
apache-airflow	https://airflow.apache.org

helm search repo airflow
NAME                  	CHART VERSION	APP VERSION	DESCRIPTION                                       
apache-airflow/airflow	1.0.0        	2.0.2      	Helm chart to deploy Apache Airflow, a platform...
```

## Create namespace
```
kubectl create namespace airflow
```

## Install airflow
#### Airflow 2.0 allows users to run multiple schedulers. This feature is only recommended for PostgreSQL
- `executor = Airflow executor`
- `flower.enabled = Enable Flower (web based tool for monitoring and administrating Celery)`
- `webserver.service.type= you can change from ClusterIP to LoadBalancer`
```
helm install airflow apache-airflow/airflow --namespace airflow \
--set airflowVersion=2.0.2 \
--set executor=CeleryExecutor \
--set defaultAirflowTag=2.0.2 \
--set redis.enabled=True \
--set flower.enabled=True \
--set webserver.service.type=ClusterIP \
--set webserver.replicas=2 \
--set scheduler.replicas=2 \
--set pgbouncer.enabled=True \
--set pgbouncer.maxClientConn=150 \
--set pgbouncer.metadataPoolSize=10 \
--set pgbouncer.resultBackendPoolSize=5 \
--set workers.replicas=5 \
--set workers.persistence.enabled=True \
--set workers.terminationGracePeriodSeconds=600 \
--set workers.persistence.size=80Gi
```

## Login to UI airflow and flower (if you use ClusterIP via port-forward) user: admin pass:admin
```
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
kubectl port-forward svc/airflow-flower 5555:5555 --namespace airflow
```

## Dockerfile and DAGS structure
```
.
├── dags
│   ├── example
│   │   └── example.py
│   └── generated
│       └── example-generated.py
└── Dockerfile
```



## Deploy new DAG
#### Build docker image
```
docker build --no-cache -t zeus-airflow .
docker tag zeus-airflow asia.gcr.io/zeus-cloud/zeus-airflow:0.6
docker push asia.gcr.io/zeus-cloud/zeus-airflow:0.6
```

#### Update airflow with new docker image and dag + auto rollback
- `--atomic = if set, upgrade process rolls back changes made in case of failed upgrade`
- `--timeout = deployment timeout if more than 180s`
- `workers.replicas= number pods worker for scale out running jobs
- `images.airflow.tag=0.6 (docker tag)`
```
helm upgrade --install --atomic --timeout 360s airflow apache-airflow/airflow --namespace airflow \
--set airflowVersion=2.0.2 \
--set executor=CeleryExecutor \
--set defaultAirflowTag=2.0.2 \
--set redis.enabled=True \
--set flower.enabled=True \
--set webserver.service.type=ClusterIP \
--set webserver.replicas=2 \
--set scheduler.replicas=2 \
--set pgbouncer.enabled=True \
--set pgbouncer.maxClientConn=150 \
--set pgbouncer.metadataPoolSize=10 \
--set pgbouncer.resultBackendPoolSize=5 \
--set workers.replicas=5 \
--set workers.persistence.enabled=True \
--set workers.terminationGracePeriodSeconds=600 \
--set workers.persistence.size=80Gi \
--set images.airflow.repository=asia.gcr.io/zeus-cloud/zeus-airflow \
--set images.airflow.tag=0.6 \
--set images.airflow.pullPolicy=Always
```

## Manual Rollback
```
helm history airflow --namespace airflow
REVISION	UPDATED                 	STATUS          	CHART        	APP VERSION	DESCRIPTION                                                  
1       	Fri Jun 11 11:58:19 2021	superseded      	airflow-1.0.0	2.0.2      	Install complete                                             
2       	Fri Jun 11 12:05:28 2021	superseded      	airflow-1.0.0	2.0.2      	Upgrade complete                                             
3       	Fri Jun 11 12:09:09 2021	pending-upgrade 	airflow-1.0.0	2.0.2      	Preparing upgrade                                            
4       	Fri Jun 11 12:15:30 2021	deployed        	airflow-1.0.0	2.0.2      	Rollback to 2                                                
5       	Fri Jun 11 12:22:32 2021	failed          	airflow-1.0.0	2.0.2      	Upgrade "airflow" failed: timed out


helm rollback airflow 4 --namespace airflow
Rollback was a success! Happy Helming!
```

## You can get Fernet Key value by running the following:
```
echo Fernet Key: $(kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode)
```
 
##### Sometime if deployment error and helm auto rollback and pods worker still ImagePullBackOff
```
kubectl delete pods -n airflow airflow-worker-0
pod "airflow-worker-0" deleted
```
 
### Uninstall airflow
```
helm delete airflow --namespace airflow
```

#### Reference
```
https://airflow.apache.org/docs/helm-chart/stable/parameters-ref.html
https://airflow.apache.org/docs/helm-chart/stable/index.html
```

